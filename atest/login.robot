*** Settings ***
Resource       resources/common.robot
Test Setup     Open Connection  ${HOST}
Test Teardown  Close All Connections

*** Variables ***
${KEY DIR}           ${LOCAL TESTDATA}${/}keyfiles
${KEY USERNAME}      testkey
${KEY}               ${KEY DIR}${/}id_rsa
${INVALID USERNAME}  invalidusername
${INVALID PASSWORD}  invalidpassword
${INVALID KEY}       ${KEY DIR}${/}id_rsa_invalid

*** Test Cases ***
Login With Valid Username And Password
    Login As Valid User

Login With Invalid Username Or Password
    [Setup]  Open Connection  ${HOST}
    Run Keyword And Expect Error  Authentication failed for user '${INVALID USERNAME}'.
    ...                           Login  ${INVALID USERNAME}  ${PASSWORD}

Login With Public Key When Valid Username And Key
    [Setup]  Open Connection  ${HOST}  prompt=${PROMPT}
    Login With Public Key  ${KEY USERNAME}  ${KEY}

Login With Public Key When Invalid Username
    Run Keyword And Expect Error  Login with public key failed for user '${INVALID USERNAME}'.
    ...    Login With Public Key  ${INVALID USERNAME}  ${KEY}

Login With Public Key When Invalid Key
    Run Keyword And Expect Error  Login with public key failed for user '${KEY USERNAME}'.
    ...    Login With Public Key  ${KEY USERNAME}  ${INVALID KEY}

Login With Public Key When Non-Existing Key
    Run Keyword And Expect Error  Given key file 'not_existing_key' does not exist.
    ...    Login With Public Key  ${KEY USERNAME}  not_existing_key

Logging In Returns Server Output
    [Setup]  Open Connection  ${HOST}
    ${output}=  Login  ${USERNAME}  ${PASSWORD}
    Should Contain  ${output}  Last login:
    ${output}=  Read
    Should Be Equal  ${output.strip()}  ${EMPTY}

Logging In Returns Server Output If Prompt Is Set
    [Setup]  Open Connection  ${HOST}  prompt=${PROMPT}
    ${output}=  Login With Public Key  ${KEY USERNAME}  ${KEY}
    Should Contain  ${output}  Last login:
    ${output}=  Read
    Should Be Equal  ${output.strip()}  ${EMPTY}

Login Using Config File
    [Setup]  Open Connection  ${TEST_HOSTNAME}  prompt=${PROMPT}
    Login  password=test  read_config=True

Login With Public Key Using Config File
    [Setup]  Open Connection   ${TESTKEY_HOSTNAME}  prompt=${PROMPT}
    Login With Public Key  read_config=True

Login With No Password
	[Setup]  Open Connection  ${HOST}  prompt=${PROMPT}
	Login  ${USERNAME_NOPASSWD}

Login With Explicit No Password
	[Setup]  Open Connection  ${HOST}  prompt=${PROMPT}
	Login  ${USERNAME_NOPASSWD}  ${EMPTY_STRING}

Login With Empty Quotes No Password
	[Setup]  Open Connection  ${HOST}  prompt=${PROMPT}
	Login  ${USERNAME_NOPASSWD}  ""

Login Using Config File Proxy Command
    [Tags]  no-gh-actions
    [Setup]  Open Connection   ${TEST_PROXY_HOSTNAME}  prompt=${PROMPT}
    ${output}=  Login  password=test  read_config=True
    Should Contain  ${output}  test@

