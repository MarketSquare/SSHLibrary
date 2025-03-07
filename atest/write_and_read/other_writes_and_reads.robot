*** Settings ***
Resource            ../resources/write_and_read_resource.robot

Suite Setup         Run Keywords    Login And Upload Test Scripts    AND    Put File    ${CORRUPTED FILE}    ${REMOTE TEST ROOT}
Suite Teardown      Remove Test Files and Close Connections


*** Test Cases ***
Write And Read Until
    ${output} =    Write    ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    Should Contain    ${output}    ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    ${output} =    Read Until    Give your name?
    Should Contain    ${output}    Give your name?
    ${output} =    Write    Mr. Ääkkönen
    Should Contain    ${output}    Mr. Ääkkönen
    ${output} =    Read Until Prompt
    Should Contain    ${output}    Hello Mr. Ääkkönen

Write And Read Until Prompt
    Write Bare    ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}    add_newline=True
    Write Bare    Mr. Ääkkönen    add_newline=True
    ${output} =    Read Until Prompt
    Should Contain    ${output}    Hello Mr. Ääkkönen

Write And Read Until Regexp
    Write    ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    ${output} =    Read Until Regexp    Give.*\\?
    Should Contain    ${output}    Give your name?
    Write Bare    Mr. Ääkkönen    add_newline=True
    Comment    Prompt needs to be escaped because it might be $
    ${output} =    Read Until Regexp    (?s).*\\${PROMPT}
    Should Contain    ${output}    Hello Mr. Ääkkönen
    Should End With    ${output}    ${PROMPT}

Write Non-String
    Write    ${1}
    ${output} =    Read Until Prompt
    Should Contain    ${output}    1

Write Bare Non-String
    Write Bare    ${False}\n
    ${output} =    Read Until Prompt
    Should Contain    ${output}    False

Write Bare Add New Line Non-String
    Write Bare    ${False}    add_newline=True
    ${output} =    Read Until Prompt
    Should Contain    ${output}    False

Write In Case Of Timeout
    Write Bare    Foo Bar And Some Other    add_newline=True
    Set Client Configuration    timeout=1
    ${status}    ${error} =    Run Keyword And Ignore Error
    ...    Read Until    This is not found
    Should Start With    ${error}    No match found for 'This is not found' in 1 second

Write Returning Stderr
    Write    ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    Read Until    Give your name?
    Write Bare    Error    add_newline=True
    ${output} =    Read Until    ${PROMPT}
    Should Contain    ${output}    Hello Error
    Should Contain    ${output}    This is Error

Write Bare And Read Until
    Write Bare    ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}    add_newline=True
    ${output} =    Read Until    name?
    Write Bare    Mr. Ääkkönen    add_newline=True
    ${output2} =    Read Until Prompt
    Should Contain    ${output}    Give your name?
    Should Contain    ${output2}    Hello Mr. Ääkkönen
    Should Contain    ${output2}    ${PROMPT}

Write Until Expected Output
    Write Until Expected Output    ${REMOTE TEST ROOT}/${REPEAT TEST SCRIPT NAME}\n
    ...    3    15 seconds    0.5 seconds
    [Teardown]    Execute Command    rm -f ${COUNTER NAME}

Write Until Expected Output In Case Of Timeout
    Run Keyword And Expect Error    No match found for '11' in 2 seconds.
    ...    Write Until Expected Output    ${REMOTE TEST ROOT}/${REPEAT TEST SCRIPT NAME}\n
    ...    11    2s    0.5s
    [Teardown]    Execute Command    rm -f ${COUNTER NAME}

Read Until Prompt With Strip Prompt
    Write Bare    echo This is a test    add_newline=True
    ${output} =    Read Until Prompt    strip_prompt=True
    Should Contain    ${output}    This is a test
    Should Not Contain    ${output}    ${PROMPT}

Read Until REGEXP Prompt With Strip Prompt
    Set Client Configuration    prompt=REGEXP:[#$]
    Write Bare    echo This is a test    add_newline=True
    ${output} =    Read Until Prompt    strip_prompt=True
    Should Contain    ${output}    This is a test
    Should Not Match Regexp    ${output}    [#$]
    [Teardown]    Set Client Configuration    prompt=${PROMPT}

Configure Session Width And Height
    Set Client Configuration    prompt=${PROMPT}    height=48    width=160
    ${conn} =    Get Connection    1
    Should Be Equal As Integers    ${conn.height}    48
    Should Be Equal As Integers    ${conn.width}    160
    Write    stty size
    ${output} =    Read Until Prompt
    Should Contain    ${output}    48 160
    [Teardown]    Set Client Configuration    height=24    width=80

Read Until With Encoding Errors On Strict
    Write Bare    cat ${REMOTE TEST ROOT}/${CORRUPTED FILE NAME}    add_newline=True
    GROUP    Read output from "cat" command
        TRY
            # "Hello" is at the end of the corrupted file
            Read Until    Hello
            Fail    READ UNTIL should have failed with expected error
        EXCEPT    *codec can't decode byte*    type=GLOB    AS    ${error_message}
            Log    Write command failed with expected error: ${error_message}
        END
    END

Read Until With Encoding Errors On Replace
    Set Client Configuration    encoding_errors=replace
    Write Bare    cat ${REMOTE TEST ROOT}/${CORRUPTED FILE NAME}    add_newline=True
    ${output} =    Read Until    Hello
    Should Contain    ${output}    Hello

Read Until With Encoding Errors On Ignore
    Set Client Configuration    encoding_errors=ignore
    Write Bare    cat ${REMOTE TEST ROOT}/${CORRUPTED FILE NAME}    add_newline=True
    ${output} =    Read Until    Hello
    Should Contain    ${output}    Hello

Read Until With Encoding Errors Set In Open Connection
    [Setup]    Run Keywords    Open Connection    ${HOST}    prompt=${PROMPT}    encoding_errors=replace    AND
    ...    Login    ${USERNAME}    ${PASSWORD}
    Write Bare    cat ${REMOTE TEST ROOT}/${CORRUPTED FILE NAME}    add_newline=True
    ${output} =    Read Until    Hello
    Should Contain    ${output}    Hello
