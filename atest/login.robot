*** Settings ***
Resource            resources/common.robot

Test Setup          Open Connection    ${HOST}
Test Teardown       Close All Connections

Test Tags           login


*** Variables ***
${KEY DIR}              ${LOCAL TESTDATA}${/}keyfiles
${KEY USERNAME}         testkey
${KEY}                  ${KEY DIR}${/}id_rsa
${INVALID USERNAME}     invalidusername
${INVALID PASSWORD}     invalidpassword
${INVALID KEY}          ${KEY DIR}${/}id_rsa_invalid


*** Test Cases ***
Login With Valid Username And Password
    Login As Valid User

Login With Invalid Username Or Password
    [Setup]    Open Connection    ${HOST}
    Run Keyword And Expect Error    Authentication failed for user '${INVALID USERNAME}'.
    ...    Login    ${INVALID USERNAME}    ${PASSWORD}

Login With Public Key When Valid Username And Key
    [Setup]    Open Connection    ${HOST}    prompt=${PROMPT}
    Login With Public Key    ${KEY USERNAME}    ${KEY}

Login With Public Key When Invalid Username
    [Documentation]    A username that does not exist on the target machine leads to a rather misleading error message about key lengths.
    ...    See: https://github.com/fabric/fabric/issues/2182#issuecomment-1362940149
    Run Keyword And Expect Error    ValueError: q must be exactly 160, 224, or 256 bits long
    ...    Login With Public Key    ${INVALID USERNAME}    ${KEY}

Login With Public Key When Invalid Key
    Run Keyword And Expect Error    Login with public key failed for user '${KEY USERNAME}'.
    ...    Login With Public Key    ${KEY USERNAME}    ${INVALID KEY}

Login With Public Key When Non-Existing Key
    Run Keyword And Expect Error    Given key file 'not_existing_key' does not exist.
    ...    Login With Public Key    ${KEY USERNAME}    not_existing_key

Login With Public Key And Disabled Algorithms
    VAR    @{pubkeys}    diffie-hellman-group16-sha512
    VAR    &{disabled_algorithms}    pubkeys=${pubkeys}
    Login With Public Key    ${KEY USERNAME}    ${KEY}    disabled_algorithms=${disabled_algorithms}

Logging In Returns Server Output
    [Setup]    Open Connection    ${HOST}
    ${output}=    Login    ${USERNAME}    ${PASSWORD}
    Should Contain    ${output}    Last login:
    ${output}=    Read
    Should Be Equal    ${output.strip()}    ${EMPTY}

Logging In Returns Server Output If Prompt Is Set
    [Setup]    Open Connection    ${HOST}    prompt=${PROMPT}
    ${output}=    Login With Public Key    ${KEY USERNAME}    ${KEY}
    Should Contain    ${output}    Last login:
    ${output}=    Read
    Should Be Equal    ${output.strip()}    ${EMPTY}

Login Using Config File
    [Setup]    Open Connection    ${TEST_HOSTNAME}    prompt=${PROMPT}
    Login    password=test    read_config=True

Login With Public Key Using Config File
    [Setup]    Open Connection    ${TESTKEY_HOSTNAME}    prompt=${PROMPT}
    Login With Public Key    read_config=True

Login With No Password
    [Setup]    Open Connection    ${HOST}    prompt=${PROMPT}
    Login    ${USERNAME_NOPASSWD}

Login With Explicit No Password
    [Setup]    Open Connection    ${HOST}    prompt=${PROMPT}
    TRY
        Login    ${USERNAME_NOPASSWD}    ${EMPTY_STRING}
    EXCEPT    Authentication failed for user '${USERNAME_NOPASSWD}'.    AS    ${ex}
        Pass Execution    Authentication with empty password failed as expected: ${ex}
    END
    Fail    Authentication with empty password should have failed

Login With Empty Quotes No Password
    [Setup]    Open Connection    ${HOST}    prompt=${PROMPT}
    Login    ${USERNAME_NOPASSWD}    ""

Login Using Config File Proxy Command
    [Tags]  no-gh-actions
    [Setup]  Open Connection   ${TEST_PROXY_HOSTNAME}  prompt=${PROMPT}
    ${output}=  Login  password=test  read_config=True
    Should Contain  ${output}  test@

Login With Disabled Algorithms
    [Setup]    Open Connection    ${HOST}    prompt=${PROMPT}
    VAR    @{pubkeys}    rsa-sha2-512    rsa-sha2-256
    VAR    &{disabled_algorithms}    pubkeys=${pubkeys}
    Login    ${USERNAME}    ${PASSWORD}    disabled_algorithms=${disabled_algorithms}

