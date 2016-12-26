*** Settings ***
Resource        ../resources/write_and_read_resource.robot
Force Tags      pybot   jybot
Suite Setup     Login And Upload Test Scripts
Suite Teardown  Remove Test Files and Close Connections


*** Test Cases ***

Write And Read Until
    ${output} =  Write  ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    Should Contain  ${output}  ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    ${output} =  Read Until  Give your name?
    Should Contain  ${output}  Give your name?
    ${output} =  Write  Mr. Ääkkönen
    Should Contain  ${output}  Mr. Ääkkönen
    ${output} =  Read Until Prompt
    Should Contain  ${output}  Hello Mr. Ääkkönen

Write And Read Until Prompt
    Write  ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    Write  Mr. Ääkkönen
    ${output} =  Read Until Prompt
    Should Contain  ${output}  Hello Mr. Ääkkönen

Write And Read Until Regexp
    Write  ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    ${output} =  Read Until Regexp  Give.*\\?
    Should Contain  ${output}  Give your name?
    Write  Mr. Ääkkönen
    Comment  Prompt needs to be escaped because it might be $
    ${output} =  Read Until Regexp  (?s).*\\${PROMPT}
    Should Contain  ${output}  Hello Mr. Ääkkönen
    Should End With  ${output}  ${PROMPT}

Write Non-String
    Write  ${1}
    ${output} =  Read Until Prompt
    Should Contain  ${output}  1

Write Bare Non-String
    Write Bare  ${False}\n
    ${output} =  Read Until Prompt
    Should Contain  ${output}  False

Write In Case Of Timeout
    Write  Foo Bar And Some Other
    Set Client Configuration   timeout=1
    ${status}  ${error} =  Run Keyword And Ignore Error
    ...                    Read Until  This is not found
    Should Start With  ${error}  No match found for 'This is not found' in 1 second

Write Returning Stderr
    Write  ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    Read Until  Give your name?
    Write  Error
    ${output} =  Read Until  ${PROMPT}
    Should Contain  ${output}  Hello Error
    Should Contain  ${output}  This is Error

Write Bare And Read Until
    Write Bare  ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}\n
    ${output} =  Read Until  name?
    Write Bare  Mr. Ääkkönen\n
    ${output2} =  Read Until Prompt
    Should Contain  ${output}  Give your name?
    Should Contain  ${output2}  Hello Mr. Ääkkönen
    Should Contain  ${output2}  ${PROMPT}

Write Until Expected Output
    Write Until Expected Output  ${REMOTE TEST ROOT}/${REPEAT TEST SCRIPT NAME}\n
    ...                          3  15 seconds  0.5 seconds
    [Teardown]  Execute Command  rm -f ${COUNTER NAME}

Write Until Expected Output In Case Of Timeout
    Run Keyword And Expect Error  No match found for '11' in 2 seconds.
    ...                           Write Until Expected Output  ${REMOTE TEST ROOT}/${REPEAT TEST SCRIPT NAME}\n
    ...                           11  2s  0.5s
    [Teardown]  Execute Command  rm -f ${COUNTER NAME}
