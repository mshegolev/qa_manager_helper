PARENT_TITLE_RELEASES = "Релизы"

MYPROJECT2_TEMPLATE_CONTENT = """
<p>&nbsp;</p>         <p></p>
<h1>1. Цель работ</h1><p>Установить релиз ${project} ${fix_version}</span></p>
<h1>2. Оценка рисков</h1>
<h1>3. Недоступные процессы, влияние на клиента/пользователя</h1>
<h1>4. Причины изменений</h1>
<h1>5. Описание плана установки</span></h1>
<h1>6. Описание плана отката</h1>
<h1>7. Тестирование</h1>
<p>Файл отчета по тестированию релиза прикреплен к задаче:  ${qa_verification_task}</p>
<h1>8. Версии совместимых систем</h1>
<h1>9. Состав релиза</h1>
${release_content}
</ul><p>&nbsp;</p>
"""
MYPROJECT1_TEMPLATE_CONTENT = """
<p>&nbsp;</p>         <p></p>
<h1>1. Цель работ</h1><p>Установить релиз ${project} ${fix_version}</span></p>
<h1>2. Оценка рисков</h1>
<h1>3. Недоступные процессы, влияние на клиента/пользователя</h1>
<h1>4. Причины изменений</h1>
<h1>5. Описание плана установки</span></h1>
<h1>6. Описание плана отката</h1>
<h1>7. Тестирование</h1>
<p>Файл отчета по тестированию релиза прикреплен к задаче:  ${qa_verification_task}</p>
<h1>8. Версии совместимых систем</h1>
<h1>9. Состав релиза</h1>
${release_content}
</ul><p>&nbsp;</p>
"""


CONFLUENCE_RELEASE_TEMPLATES = {
    "MYPROJECT1": MYPROJECT1_TEMPLATE_CONTENT,
    "MYPROJECT2": MYPROJECT2_TEMPLATE_CONTENT
}

PERFORMANCE_RELEASE_TEMPLATE = """

[Project_name_here]

Load/Performance Test Plan

Version [Version_number]
Author: [Your_name_here]

[Your_Company_name]
[Street_name_1]
[Street_name_2]
[City_Zip_Country]
[Phone_number]
[URL] 

Audit Trail:

Date	Version	Name	Comment
			
 		 	 
 		 	 

Table of Contents
TABLE OF CONTENTS	2
1.	REFERENCE DOCUMENTS	3
1.	SCOPE	3
2.	APPROACH	3
3.	LOAD TEST TYPES AND SCHEDULES	3
4.	PERFORMANCE/CAPABILITY GOALS	3
5.	LOAD TESTING PROCESS, STATUS REPORTING, FINAL REPORT	4
6.	BUG REPORTING AND REGRESSION INSTRUCTIONS	5
7.	TOOLS USED	5
8.	TRAINING NEEDS	5
9.	LOAD DESCRIPTIONS	5
10.	SYSTEM UNDER TEST ENVIRONMENT	6
11.	EXCLUSIONS	6
12.	TEST DELIVERABLES	6
13.	BUDGET/RESOURCE	6
14.	TEAM MEMBERS AND RESPONSIBILITIES	7
15.	LIST OF APPENDICES	7
16.	TEST PLAN APPROVAL	7
APPENDIX 1	USER SCENARIO TEST SUITE	8
APPENDIX 2	CONCURRENCY LOAD TESTING SUITE	8
APPENDIX 3	DATA ELEMENT FROM LOAD TEST	8
APPENDIX 4	TEST SCRIPTS – REQUIRES WEBLOAD OR TEXT EDITOR – IN JAVASCRIPT	8
APPENDIX 5	ERROR OR WEB SERVER FAILURES.	8
APPENDIX 5	WEB MONITORING DATA.	8

1.	Reference Documents

Reference information used for the development of this plan including:
•	Business requirements
•	Technical requirements
•	Test requirements
•	…and other dependencies

1.	Scope	

What does this document entail?
What is being tested?
What is the overall objective of this plan? For examples:
•	To document test objectives, test requirements, test designs, test procedures, and other project management information
•	To solicit feedback and build consensus
•	To define development and testing deliverables
•	To secure commitment and resources for the test effort

2.	Approach	

The high-level description of the testing approach that enables us to cost effectively meet the expectation stated in the Scope section. 
3.	Load Test Types and Schedules	

Specify the test types (with definition for each) to run:
•	Acceptance test
•	Baseline test
•	2B1 load test
•	Goal-reaching test
•	Spike test
•	Burstiness test
•	Stress test
•	Scalability test
•	Regression test
•	Benchmark test

Be specific:
•	Specify what tests you will run
•	Estimate how many cycles of each test you will run
•	Schedule your tests ahead of time
•	Specify by what criteria you will consider the SUT to be ready-for-test
•	Forward thinking: Determine and communicate the planned tests and how the tests are scheduled
4.	Performance/Capability Goals

Identify goals:
•	Percentage of requested static pages that must meet the acceptable response time?
•	Percentage of requested scripts that must meet the acceptable response time?
•	The baseline multiplier (2x, 4x, ...) that the system must be capable of handling?
•	The spike ratio that the system must be capable of handling?
•	The peak ratio that the system must be capable of handling?
•	The burstiness ratio that the system must be capable of handling?
•	Tolerance ratio: Imposed load ? 25 %?
•	Safety ratio: Imposed load x 2?
•	Spike ratio: Imposed load x 3?
•	Burstiness ratio: Imposed load x 5?
•	Increase the load by multiplying the load baseline by 1x, 2x, 3x, 4x, Nx gradually until unacceptable response time is reached.

Other questions to consider:
•	What is response time?
•	What is acceptable response time?
•	Which metrics should we collect?
•	What is the correlation between demand and increased load?
•	How do we determine which components are problematic?
•	How do we correlate financial implications?
 

5.	Load Testing Process, Status Reporting, Final Report

Describe the testing and reporting procedures. For example:
•	The internal test team will execute all created scripts.  These Scripts will be generated and executed against the system at least three times.  We will execute these scripts again, after subsequent hardware, software, or other fixes are introduced.  

•	Test team will baseline load as follows:
•	Load Test Team will test Nile.com with 1000 Simultaneous Clients/Users, and report back on the following metrics:
•	Response Time each transaction hitting the Web site.
•	Any web or database server errors as reported in the data log.
•	Round time
•	Failed Web Transactions
•	There will be Status Reports sent to Team Lead detailing:
•	Performance tests run
•	Performance metrics collected
•	Performance Errors and status
•	Number of Bugs Entered
•	Status Summary 
•	Additional load testing, if needed. 
•	The Final Report will include summary bug counts, overall performance assessment, and test project summary items.

Additional Information to be provided by Development Team:
1.	Build Schedule
2.	Acceptance test criteria
3.	Deployment Plans

6.	Bug Reporting and Regression Instructions

Describe the bug reporting process and the fix/change regression test procedures.

7.	Tools Used

State the tool solutions for the project:
•	Load testing tools
•	Monitoring tools
Tool Options:
•	Product vs. Application Service Provider (ASP)
•	Freeware
•	Lease or rent
•	Purchase
•	Build
•	Outsourcing (testing with virtual client licensing included)

8.	Training Needs

Training programs to be provided to the team to enable successful planning and execution.


9.	Load Descriptions

Server-based
•	Number of users and/or sessions
•	Average session time
•	Number of page views
•	Average page views per session
•	Peak period (e.g., 75% of traffic is from 11:00 AM-4:00 PM)
•	Number of hits
•	Average page size
•	Most requested pages
•	Average time spend on page
•	New users vs. returning users
•	Frequency of visits (e.g., 75% of users made one visit)
•	Demographics
•	Client information such as browser, browser version, Java script support, Java script enable/disable, and so on.

User-based
•	Number of users
•	Session length
•	User activities and frequency of activities per session
•	Think/Read/Data-input time
•	Percentage by functional group
•	Percentage by human speed 
•	Percentage by human patience (cancellation rates)
•	Percentage by domain expertise (speed)
•	Percentage by familiarity (speed)
•	Percentage by demographics (arrival rates)

Other questions to consider:
•	What is the definition of “workload”? 
•	How do we size the workload?
•	What is the expected workload?
•	What’s the mix ratio of static pages vs. code?
•	What is the definition of “increased load”?
•	What is future growth? Can it be quantified?
•	What is the definition of scalability?


10.	System Under Test Environment

Specifying mixes of system hardware, software, memory, network protocol, bandwidth, etc.
•	Network access variables: For example, 56K modem, 128K Cable modem, T1, etc.
•	Demographic variables: For example San Francisco, Los Angeles, Chicago, New York, Paris, London, etc.
•	ISP infrastructure variables: For example, first tier, second tier, etc.
•	Client baseline configurations
•	Computer variables
•	Browser variables
•	Server baseline configurations
•	Computer variables
•	System architecture variables and diagrams

Other questions to consider asking:
•	What is the definition of “system”?
•	How many other users are using the same resources on the system under test (SUT)?
•	Are you testing the SUT in its complete, real-world environment (with load balances, replicated database, etc.)?
•	Is the SUT inside or outside the firewall?
•	Is the load coming from the inside or outside of the firewall?

11.	Exclusions

Set clear expectations—State which goals will be outside of the scope of this testing. For example:
•	Content accuracy or appropriateness testing is out of the scope of this plan.
•	The integration of any major third party components (for example a search engine, credit card processor, or mapping component) with the site will be tested, though the scope of the project does not include in-depth functional testing of these components.
•	Internationalization
•	Compatibility Testing

12.	Test Deliverables

•	This test plan
•	Performance testing goals
•	Workload definitions
•	User scenario designs
•	Performance test designs
•	Test procedures
•	System baseline/System-under-test configurations
•	Metrics to collect
•	Tool evaluation and selection reports (first time, or as needed)
•	Test scripts/suites
•	Test run results
•	Analysis reports against the collected data
•	Performance related error reports (e.g., failed transactions)
•	Functional bug reports (e.g., data integrity problems)
•	Periodic status reports
•	Final report

13.	Budget/Resource
Monetary requirements for equipment and people to complete the plan.   

14.	Team Members and Responsibilities
 Project team members, their responsibilities and contact information.

15.	List of Appendices 

Specific test case, test design and test script information to be added as we go. Here are a few examples:
•	Real-World User-Level Test Suite
•	Concurrency Test Suite
•	Data Elements
•	Test Scripts
•	Error Reports
•	Web Monitoring Data
16.	Test Plan Approval

Business Approval

__________________________________________________			 	_____________
[Name/Title]								Date



Testing Approval

___________________________________________________				_____________
[Name/Title]								Date

 
Appendices
Appendix 1	User Scenario Test Suite


Appendix 2	Concurrency Load Testing Suite


Appendix 3	Data Element from Load Test


Appendix 4	Test Scripts – Requires Webload or Text Editor – IN JAVASCRIPT


Appendix 5	Error or Web Server Failures.


Appendix 5	Web Monitoring Data.



"""
