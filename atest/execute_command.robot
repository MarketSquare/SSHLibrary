*** Settings ***
Default Tags      pybot   jybot
Resource        resources/shell.robot
Suite Setup     Login And Upload Test Scripts
Suite Teardown  Remove Test Files And Close Connections
Library         OperatingSystem  WITH NAME  OS

*** Test Cases ***
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
    ...                              Execute Command    ping localhost    timeout=2s

Execute Command With Legacy Stdout And Stderr Config
    ${stdout}  ${stderr} =  Execute Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ...                     Both
    Should Be Equal  ${stdout}  This is stdout
    Should Be Equal  ${stderr}  This is stderr

Execute Command With Robot Timeout
   [Documentation]   FAIL Test timeout 500 milliseconds exceeded.
   [Timeout]   0.5 seconds
   Execute Command     cat

Execute Command With Huge Output
   [Tags]      pybot        # this fails with jybot
   [Timeout]   5 seconds
   Execute Command     echo 'foo\\nbar\\n' > file.txt
   Execute Command     for i in {1..20}; do cat file.txt file.txt > file2.txt && mv file2.txt file.txt; done
   Execute Command     cat file.txt
   [Teardown]  Execute Command     rm file.txt

Execute Sudo Command With Correct Password
    [Tags]     linux
    ${stdout} =  Execute Command  -k pwd   sudo=True  sudo_password=test
    Should Contain  ${stdout}   ${REMOTE HOME TEST}

Execute Sudo Command With Incorrect Password
    [Tags]     linux
    ${stdout} =  Execute Command  -k pwd   sudo=True  sudo_password=test123
    Should Not Contain  ${stdout}  ${REMOTE HOME TEST}

Execute Time Consuming Sudo Command
    [Tags]     linux
    ${stdout} =  Execute Command  -k sleep 5; echo cat   sudo=True  sudo_password=test
    Should Contain  ${stdout}  cat
	