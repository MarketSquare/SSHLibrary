*** Settings ***
Force Tags      pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login And Upload Test Files
Suite Teardown  Remove Test Files and Close Connections
Library         Collections

*** Test Cases ***
List Directories Using Absolute Path
    ${expected} =  Create List  ${SUBDIRECTORY NAME}
    ${listing} =  List Directories In Directory  ${REMOTE TEST ROOT}
    Lists Should Be Equal  ${listing}  ${expected}

List Directories Using Relative Path
    ${expected} =  Create List  ${SUBDIRECTORY NAME}
    ${listing} =  List Directories In Directory  ${REMOTE TEST ROOT NAME}
    Lists Should Be Equal  ${listing}  ${expected}

List Directories Using Pattern
    ${expected} =  Create List  ${SUBDIRECTORY NAME}
    ${listing} =  List Directories In Directory  ${REMOTE TEST ROOT}  pattern=aaä*
    Lists Should Be Equal  ${listing}  ${expected}

List Directories Using Current Working Directory
    ${listing} =  List Directories In Directory  .
    Should Contain  ${listing}  ${REMOTE TEST ROOT NAME}

List Directories Using Symlink As Path
    [Setup]  Execute Command  ln -s ${REMOTE TEST ROOT} symlink
    ${expected} =  Create List  ${SUBDIRECTORY NAME}
    ${listing} =  List Directories In Directory  symlink
    Lists Should Be Equal  ${listing}  ${expected}
    [Teardown]  Execute Command  rm -f symlink

List Directories Using Non-ASCII Characters In Path
    ${expected} =  Create List  ${DIRECTORY WITH EMPTY SUBDIRECTORY}
    ${listing} =  List Directories In Directory  ${REMOTE TEST ROOT}${/}${SUBDIRECTORY NAME}
    Lists Should Be Equal  ${listing}  ${expected}

List Directories With Absolute Paths Using Absolute Path
    ${expected} =  Create List  ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}
    ${listing} =  List Directories In Directory  ${REMOTE TEST ROOT}  absolute=True
    Lists Should Be Equal  ${listing}  ${expected}

List Directories With Absolute Paths Using Relative Path
    ${expected} =  Create List  ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}
    ${target} =  Set Variable  ${REMOTE TEST ROOT NAME}
    ${listing} =  List Directories In Directory  ${target}  absolute=True
    Lists Should Be Equal  ${listing}  ${expected}

List Directories With Absolute Paths Using Current Working Directory
    ${listing} =  List Directories In Directory  .  absolute=True
    Should Contain  ${listing}  ${REMOTE TEST ROOT}

List Directories With Absolute Paths Using Pattern
    ${expected} =  Create List  ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}
    ${listing} =  List Directories In Directory  ${REMOTE TEST ROOT}  pattern=aaä*
    ...           absolute=True
    Lists Should Be Equal  ${listing}  ${expected}

List Directories With Absolute Paths Using Symlink As Path
    [Setup]  Execute Command  ln -s ${REMOTE TEST ROOT} symlink
    ${expected} =  Create List  ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}
    ${listing} =  List Directories In Directory  symlink  absolute=True
    Lists Should Be Equal  ${listing}  ${expected}
    [Teardown]  Execute Command  rm -f symlink

List Directories Should Fail When Source Path Does Not Exists
    ${target} =  Set Variable  not_exists
    Run Keyword And Expect Error  There was no directory matching '${target}'.
    ...                           List Directories In Directory  ${target}
