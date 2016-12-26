*** Settings ***
Force Tags      pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login And Upload Test Files
Suite Teardown  Remove Test Files and Close Connections
Resource        resources/sftp.robot
Library         Collections

*** Test Cases ***
List Files Using Absolute Path
    ${expected} =  Create List
    ...                         ${FILE WITH NEWLINES NAME}
    ...                         ${FILE WITH SPECIAL CHARS NAME}
    ...                         ${TEST FILE NAME}
    ${listing} =  List Files In Directory  ${REMOTE TEST ROOT}
    Lists Should Be Equal  ${listing}  ${expected}

List Files Using Relative Path
    ${expected} =  Create List
    ...                         ${FILE WITH NEWLINES NAME}
    ...                         ${FILE WITH SPECIAL CHARS NAME}
    ...                         ${TEST FILE NAME}
    ${listing} =  List Files In Directory  ${REMOTE TEST ROOT NAME}
    Lists Should Be Equal  ${listing}  ${expected}

List Files Using Pattern
    ${expected} =  Create List  ${FILE WITH NEWLINES NAME}
    ${listing} =  List Files In Directory  ${REMOTE TEST ROOT}  pattern=*newlines.txt
    Lists Should Be Equal  ${listing}  ${expected}

List Files Using Current Working Directory
    ${listing} =  List Files In Directory  .
    Should Not Contain  ${listing}  ${REMOTE TEST ROOT}

List Files Using Symlink As Path
    [Setup]  Execute Command  ln -s ${REMOTE TEST ROOT} symlink
    ${expected} =  Create List
    ...                         ${FILE WITH NEWLINES NAME}
    ...                         ${FILE WITH SPECIAL CHARS NAME}
    ...                         ${TEST FILE NAME}
    ${listing} =  List Files In Directory  symlink
    Lists Should Be Equal  ${listing}  ${expected}
    [Teardown]  Execute Command  rm -f symlink

List Files With Non-ASCII Characters In Path
    ${expected} =  Create List  ${FILE WITH NON-ASCII NAME}
    ${listing} =  List Files In Directory  ${REMOTE TEST ROOT}${/}${SUBDIRECTORY NAME}
    Lists Should Be Equal  ${listing}  ${expected}

List Files With Absolute Paths Using Absolute Path
    ${expected} =  Create List
    ...                 ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    ...                 ${REMOTE TEST ROOT}/${FILE WITH SPECIAL CHARS NAME}
    ...                 ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${listing} =  List Files In Directory  ${REMOTE TEST ROOT}  absolute=True
    Lists Should Be Equal  ${listing}  ${expected}

List Files With Absolute Paths Using Relative Path
    ${expected} =  Create List
    ...                 ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    ...                 ${REMOTE TEST ROOT}/${FILE WITH SPECIAL CHARS NAME}
    ...                 ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${listing} =  List Files In Directory  ${REMOTE TEST ROOT NAME}  absolute=True
    Lists Should Be Equal  ${listing}  ${EXPECTED}

List Files With Absolute Paths Using Pattern
    ${expected} =  Create List
    ...                 ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    ...                 ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${listing} =  List Files In Directory  ${REMOTE TEST ROOT}  pattern=?est*
    ...           absolute=True
    Lists Should Be Equal  ${listing}  ${expected}

List Files With Absolute Paths Using Current Working Directory
    ${listing} =  List Files In Directory  .  absolute=True
    Should Not Contain  ${listing}  ${REMOTE TEST ROOT}

List Files With Absolute Paths Using Symlink As Path
    [Setup]  Execute Command  ln -s ${REMOTE TEST ROOT} symlink
    ${expected} =  Create List
    ...                 ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    ...                 ${REMOTE TEST ROOT}/${FILE WITH SPECIAL CHARS NAME}
    ...                 ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${listing} =  List Files In Directory  symlink  absolute=True
    Lists Should Be Equal  ${listing}  ${expected}
    [Teardown]  Execute Command  rm -f symlink

List Files Should Fail When Source Path Not Exists
    ${target} =  Set Variable  not_exists
    Run Keyword And Expect Error  There was no directory matching '${target}'.
    ...                           List Files In Directory  ${target}
