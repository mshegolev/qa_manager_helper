import argparse
import os
import re
import time
from argparse import ArgumentParser
from datetime import datetime, timedelta

import gitlab
from gitlab import GitlabGetError
from gitlab.v4.objects import ProjectCommitManager

from utils.constants import (
    GITLAB_BRANCH_PATTERN,
    GITLAB_RELEASE_BRANCH,
    GITLAB_RELEASE_PATTERN,
    GITLAB_URL,
    PROJECT_NAME_WITH_NAMESPACE,
)

CI_JOB_TOKEN = os.environ["CI_JOB_TOKEN"]
SSL_CERT = os.path.normpath(os.path.abspath(__file__) + "/../../../") + "/ssl/"


class Envs:
    prod = "prod"
    dev = "dev"
    stage = "stage"
    all = [dev, prod, stage]

    def __str__(self):
        return self.dev + "," + self.prod


class JobStatus(object):
    SUCCESS = "success"
    RUNNING = "running"


def get_days_ago(days_ago):
    time_lag = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return time_lag


class Do:
    def __init__(self, branch="", version="", environment=""):
        self.branch = branch
        self.version = version
        self.environment = environment
        self.gl = gitlab.Gitlab(url=GITLAB_URL, private_token=CI_JOB_TOKEN, ssl_verify=SSL_CERT)
        self.project = self.gl.projects.get(PROJECT_NAME_WITH_NAMESPACE)

    def get_tags(self, tag="", env_name=""):
        result_tags = []
        tags = self.project.tags.list(get_all=True)
        if tag and env_name:
            tag_name = env_name + "/" + tag
            result_tags = self._compare_tag_in_tag_name(tag_name=tag_name, tags=tags, compare="==")
        elif tag and env_name == "":
            tag_name = tag
            result_tags = self._compare_tag_in_tag_name(tag_name=tag_name, tags=tags, compare="in")
        elif tag == "" and env_name:
            tag_name = env_name + "/"
            result_tags = self._compare_tag_in_tag_name(tag_name=tag_name, tags=tags, compare="in")
        return result_tags

    @staticmethod
    def _compare_tag_in_tag_name(tag_name, tags, compare="in") -> list:
        assert compare in ("in", "=="), 'Можно сравнивать только по вхождению "in" и равенству "==".'
        result_tags = []
        for tag in tags:
            if compare == "in":
                if tag_name == tag.name:
                    result_tags.append(tag.name)
            if compare == "==":
                if tag_name == tag.name:
                    result_tags.append(tag.name)
                    break
        return result_tags

    def get_branches(self):
        return self.project.branches.list(get_all=True)

    def is_branch_exist(self, branch_name=GITLAB_RELEASE_BRANCH) -> bool:
        try:
            return self.project.branches.get(branch_name) is not None
        except GitlabGetError:
            return False

    @staticmethod
    def validation_branch_name(release_name):

        assert re.fullmatch(
            GITLAB_BRANCH_PATTERN, release_name
        ), f"Название ветки не соответствует паттерну {GITLAB_BRANCH_PATTERN}"

    @staticmethod
    def validation_tag_name(tag_name, quite_mode=False):

        if quite_mode:
            return re.fullmatch(GITLAB_RELEASE_PATTERN, tag_name) is not None
        assert re.fullmatch(
            GITLAB_RELEASE_PATTERN, tag_name
        ), f"Название тега не соответствует паттерну {GITLAB_RELEASE_PATTERN}"

    def create_branch(self, branch_name=GITLAB_RELEASE_BRANCH, dry_run=True) -> bool:
        self.validation_branch_name(GITLAB_RELEASE_BRANCH)
        try:
            if not self.is_branch_exist(branch_name):
                if dry_run:
                    print(f"{time.asctime()}: Branch will crated: {branch_name} from master.")
                else:
                    self.project.branches.create({"branch": branch_name, "ref": "master"})
                    print(f"{time.asctime()}: Branch was crated: {branch_name} from master.")
                return self.is_branch_exist(branch_name)

        except GitlabGetError:
            return False

    def create_annotated_tag(self, tag_name, release_branch, annotation_tag=False, rc=False, dry_run=True) -> bool:
        self.validation_tag_name(tag_name)
        if self.is_tag_exist(tag_name):
            print(f"{time.asctime()}: Аннотированный тег уже существует: {tag_name}")

        self.check_last_annotated_tag(release_branch, tag_name)
        message = tag_name if annotation_tag else ""
        return self._create_tag(tag_name=tag_name, ref=release_branch, message=message, dry_run=dry_run)

    def _create_tag(self, tag_name, ref, message="", dry_run=True) -> bool:
        try:
            if not self.is_tag_exist(tag_name):
                print(f"{time.asctime()}: Создаем тег: ", {"tag_name": tag_name, "ref": ref, "message": message})
                if dry_run:
                    return False
                else:
                    self.project.tags.create({"tag_name": tag_name, "ref": ref, "message": message})
                    print(f"{time.asctime()}: Pipeline: {self.get_pipeline_url(tag=tag_name)}")
                    return True
        except GitlabGetError:
            return False

    def check_last_annotated_tag(self, branch_name, tag_name):
        tags = self._get_last_annotated_tag(branch_name)
        if len(tags) == 0:
            first_tag = "v" + GITLAB_RELEASE_BRANCH.split("-")[1] + ".0"
            assert tag_name != first_tag, f"Первый аннотированый тег должен быть {first_tag}"
        if not self.is_last_commit_have_tag(tag_name=tags[-1], release=branch_name):
            print(f"{time.asctime()}: Нужно установить тег на последний комит в ветке")
        else:
            print(f"{time.asctime()}: Последний коммит в ветке {branch_name} имеет аннотированный тег {tag_name}")
        return self

    def get_all_tags(self):
        return self.project.tags.list(get_all=True)

    def _get_last_annotated_tag(self, release=GITLAB_RELEASE_BRANCH) -> list:
        self.validation_branch_name(GITLAB_RELEASE_BRANCH)
        release_tags = []
        last_tag = ""
        release_tag = "v" + release.replace("release-", "")
        tags = self.get_all_tags()
        for tag in tags:
            if release_tag in tag.name and tag.message and self.validation_tag_name(tag.name, quite_mode=True):
                release_tags.append(tag.name)
        release_tags.reverse()
        if len(release_tags) > 0:
            last_tag = [release_tags[-1]]
        print(f"{time.asctime()}: Последний аннотированный тег {last_tag}, из всех тегов:", release_tags)
        return release_tags

    def is_last_commit_have_tag(self, tag_name, release):
        commit = self.project.commits.get(release)
        tags = commit.refs("tag")
        for _ in tags:
            if tag_name == _["name"]:
                return True
        return False

    def is_tag_exist(self, tag_name: str, commit: ProjectCommitManager = None) -> bool:
        if commit:
            tags = commit.refs("tag")
            for tag in tags:
                if tag_name == tag["name"]:
                    return True
        else:
            tags = self.get_all_tags()
            for tag in tags:
                if tag_name == tag.name:
                    return True
        return False

    def get_last_commit(self, branch=GITLAB_RELEASE_BRANCH):
        return self.project.commits.get(id=branch)

    def check_dry_run(self, dry_run, timeout=30):
        if dry_run:
            print(
                f"{time.asctime()}: Запуск в холостую активирован. "
                "Отправьте письмо если начинаете работы в продуктивной среде."
            )
        elif not dry_run:
            print(
                f"{time.asctime()}: Выбран режим записи, релиз будет установлен, теги будут установлены, "
                f"у вас есть {timeout} секунд чтобы отменить действие нажав  ctrl+c!!!"
            )
            for i in range(timeout, -1, -1):
                print(f"{time.asctime()}: Запуск через: {i} сек.")
                time.sleep(1)
            print(f"{time.asctime()}: Запуск!!!")

    def deploy(self, environment, version, dry_run=True):
        deployment_tag = "/".join([environment, version])
        assert environment in Envs.all, f"Можно деплоить только на известные окружения {Envs.all}"
        cmd = (
            f"python3 utils/gitlab/deployment.py -r {self.branch}-v {self.version} -e {self.environment} "
            f"--no-dry-run --annotation-tag --no-deploy"
        )
        if not self.is_tag_exist(version):
            raise NameError(
                f"Тег {version} не найден, сначала нужно создать аннотированный тег, "
                f"для этого нужно перезапустить установку: \n {cmd} \n"
            )

        if self.is_tag_exist(deployment_tag):
            self.redeploy(environment=environment, version=version, dry_run=dry_run)
        else:
            ref = self.project.commits.get(id=version).short_id
            self._create_tag(tag_name=deployment_tag, ref=ref, message="", dry_run=dry_run)

    def redeploy(self, environment, version, dry_run=True) -> bool:
        tag = "/".join([environment, version])
        assert self.is_tag_exist(tag), f"Деплоймента еще небыло: {tag}"
        pipeline_id = self.get_pipeline_id(tag)
        job_id = self.get_job_id(environment, pipeline_id)
        job = self.project.jobs.get(job_id)
        print(f"{time.asctime()}: Job url: ", job.web_url)
        if dry_run:
            return False
        else:
            job.retry()
        return True

    def get_job_id(self, environment, pipeline_id) -> int | None:
        pipeline = self.project.pipelines.get(id=pipeline_id)
        jobs = pipeline.jobs.list(get_all=True)
        job_name = "deploy-" + environment
        for job in jobs:
            if job_name == job.name:
                return job.jira_id
        return None

    def get_pipeline_id(self, tag) -> int | None:
        if not self.is_tag_exist(tag):
            return None
        commit = self.project.commits.get(tag)
        pipeline_id = commit.last_pipeline.get("id")
        return pipeline_id

    def get_pipeline_url(self, tag) -> int | None:
        if not self.is_tag_exist(tag):
            return None
        commit = self.project.commits.get(tag)
        return commit.last_pipeline.get("web_url")

    def get_last_deployed_version(self, env_name=None, days_ago=40):
        last_deployed_tag = ""
        job_name = "deploy-" + env_name
        time_ago = get_days_ago(days_ago)

        tags = self.get_tags(tag="", env_name=env_name)

        pipelines = self.project.pipelines.list(updated_after=time_ago, tags=tags, get_all=True)
        print(f"{time.asctime()}: Всего было найдено {len(pipelines)} pipelines, c даты {time_ago}.")

        for pipeline in pipelines:
            if last_deployed_tag:
                break
            jobs = pipeline.jobs.list(get_all=True)
            for job in jobs:
                if job_name == job.name:
                    if JobStatus.RUNNING == job.status:
                        print(f"{time.asctime()}: Job: {job.name} запущена, {job.web_url}. ")
                    if JobStatus.SUCCESS == job.status:
                        print(f"{time.asctime()}: Последний тег {job.ref=}, задеплоенная джоба {job.web_url}.")
                        last_deployed_tag = job.ref
        if last_deployed_tag:
            print(f"{time.asctime()}: Джоба для отката на предудущую версию {job.ref}, {job.web_url}")
        else:
            print(
                f"{time.asctime()}: Последний успешный деплой для {env_name}, не был найден. "
                f"Рекомендуется увеличить период поиска. Сейчас ищем за {days_ago} дней назад, с даты {time_ago}."
            )

        return last_deployed_tag


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-r", "--release", dest="release", required=True, help="set release branch name, example: release-1.0"
    )
    parser.add_argument("-v", "--version", dest="version", required=True, help="set version, example: v1.0.0")
    parser.add_argument(
        "-e", "--environment", dest="environment", required=True, choices=Envs.all, help="set version, example: dev"
    )
    parser.add_argument(
        "-a",
        "--annotation-tag",
        dest="annotation_tag",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="set annotation-tag, example: --no-annotation-tag",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        dest="dry_run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="set dry-run, example: --dry-run",
    )
    parser.add_argument(
        "-D",
        "--deploy",
        dest="deploy",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="set only-deploy, example: deploy",
    )

    args = parser.parse_args()
    for _ in args._get_kwargs():
        globals()[f"{_[0]}"] = _[1]
    return globals()


if __name__ == "__main__":
    deploy = annotation_tag = release = version = environment = dry_run = None
    args = parse_args()

    # Create branch
    do = Do(branch=release, version=version, environment=environment)
    assert_message = (
        f"Запрещено устанавливать новую версию {version}, " f"если не найдена джоба для отката на предудущую версию"
    )
    if environment == Envs.prod:
        assert do.get_last_deployed_version(env_name=environment, days_ago=40), assert_message

    do.check_dry_run(dry_run, 10)
    do.create_branch(branch_name=release, dry_run=dry_run)

    # Create annotated tag
    if annotation_tag:
        do.create_annotated_tag(
            tag_name=version, release_branch=release, annotation_tag=True, rc=False, dry_run=dry_run
        )

    # Deployment
    if deploy:
        do.deploy(environment=environment, version=version, dry_run=dry_run)

    print(f"{time.asctime()}: Работа скрипта завершена.")
