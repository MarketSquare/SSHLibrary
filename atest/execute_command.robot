*** Settings ***
Resource        resources/shell.robot
Suite Setup     Login And Upload Test Scripts
Suite Teardown  Remove Test Files And Close Connections
Library         OperatingSystem  WITH NAME  OS
Library         DateTime

Test Tags       shell    execute_command

*** Test Cases ***
Execute Timeout
    [Documentation]  FAIL  SSHClientException: Timed out in 3 seconds
    ...              LOG  1:2  INFO  GLOB:  *Command no. 1*Command no. 2*Command no. 3*
    TRY
        Execute Command  for i in {1..5}; do echo "Command no. $i"; sleep 1; done  timeout=3s  output_if_timeout=True
    EXCEPT  SSHClientException: Timed out in 3 seconds
        Pass Execution    Test passed: Command successfully timed out after 3 seconds.
    EXCEPT    AS    ${exception}
        Fail    Unexpected exception: ${exception}
    END
    Fail    Expected timeout did not occur.

Execute Command With Defaults
    ${stdout} =  Execute Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    Should Be Equal  ${stdout}  This is stdout

Execute Command And Return Stderr
    ${stderr} =  Execute Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ...          return_stdout=false  return_stderr=yes
    Should Be Equal  ${stderr}  This is stderr

Execute Command And Return Rc
    ${rc} =  Execute Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ...           return_stdout=False  return_rc=${true}
    Should Be Equal As Integers  ${rc}  0

Execute Command And Return All Values
    ${stdout}  ${stderr}  ${rc} =  Execute Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ...                            foo  bar  baz
    Should Be Equal  ${stdout}  This is stdout
    Should Be Equal  ${stderr}  This is stderr
    Should Be Equal As Integers  ${rc}  0

Execute Command With Output Containing Newlines
    ${result} =  Execute Command  echo -e "\n\nfoo"
    Should Be Equal  ${result}  \n\nfoo

Execute Command With Multiple Statements
    ${result} =  Execute Command  echo "foo\n"; echo RC=$?
    Should Be Equal  ${result}  foo\n\nRC=0

Executing Command With Non-ASCII characters
    ${result}=  Execute Command  echo 'aaääöö'
    Should Contain  ${result}  aaääöö

Execute Command With Legacy Stdout Config
    ${stdout} =  Execute Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ...                           STDout
    Should Be Equal  ${stdout}  This is stdout

Execute Command With Legacy Stderr Config
    ${stderr} =  Execute Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ...                           stderr
    Should Be Equal  ${stderr}  This is stderr

Execute Command With Timeout Argument
    Run Keyword And Expect Error     SSHClientException: Timed out in * seconds
    ...                              Execute Command    cat               timeout=1s
    Run Keyword And Expect Error     SSHClientException: Timed out in * seconds
    ...                              Execute Command    sleep 5    timeout=2s

Execute Command With Legacy Stdout And Stderr Config
    ${stdout}  ${stderr} =  Execute Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ...                     Both
    Should Be Equal  ${stdout}  This is stdout
    Should Be Equal  ${stderr}  This is stderr

Execute Command With Robot Timeout
   [Documentation]   FAIL Test timeout 500 milliseconds exceeded.
   [Timeout]   0.5 seconds
   Execute Command     cat
   [Teardown]    Run Keyword If   ${TEST_MESSAGE} == 'Test timeout 500 milliseconds exceeded.'  Pass Execution  Test passed: Command successfully timed out after 500 milliseconds.

Execute Command With Huge Output
   [Timeout]   5 seconds
   Execute Command     echo 'foo\\nbar\\n' > file.txt
   Execute Command     for i in {1..20}; do cat file.txt file.txt > file2.txt && mv file2.txt file.txt; done
   Execute Command     cat file.txt
   [Teardown]  Execute Command     rm file.txt

Execute Sudo Command With Correct Password
    ${stdout} =  Execute Command  -k pwd   sudo=True  sudo_password=test
    Should Be Equal  ${stdout}   ${REMOTE HOME TEST}

Execute Sudo Command With Incorrect Password
    ${stdout} =  Execute Command  -k pwd   sudo=True  sudo_password=test123
    Should Not Contain  ${stdout}  ${REMOTE HOME TEST}

Execute Time Consuming Sudo Command
    ${stdout} =  Execute Command  -k sleep 5; echo cat   sudo=True  sudo_password=test
    Should Contain  ${stdout}  cat

Execute Command With Invoke Subsystem
    ${stdout} =  Execute Command  subsys  invoke_subsystem=yes
    Should Be Equal  ${stdout}  Subsystem invoked.

Execute Command With Timeout
    Run Keyword and Expect Error  *Timed out in 5 seconds  Execute Command  sleep 10  timeout=5s

Execute Command In Certain Amount Of Time
    ${start_time}=  Get Current Date  result_format=epoch  exclude_millis=True
    Execute Command  for i in {1..3}; do echo "Command no. $i"; sleep 1; done  timeout=5s
    ${end_time}=  Get Current Date  result_format=epoch  exclude_millis=True
    ${execution_time}=  Subtract Time From Time  ${end_time}  ${start_time}
    Should Be True  ${execution_time} < 5
