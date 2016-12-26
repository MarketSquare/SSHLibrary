*** Settings ***
Force Tags      pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login And Upload Test Files
Suite Teardown  Remove Test Files and Close Connections
Library         Collections

*** Test Cases ***
List Content Using Absolute Path
    ${expected} =  Create List
    ...                         ${FILE WITH NEWLINES NAME}
    ...                         ${SUBDIRECTORY NAME}
    ...                         ${FILE WITH SPECIAL CHARS NAME}
    ...                         ${TEST FILE NAME}

    ${listing} =  List Directory  ${REMOTE TEST ROOT}
    Lists Should Be Equal  ${listing}  ${expected}

List Content Using Relative Path
    ${expected} =  Create List
    ...                         ${FILE WITH NEWLINES NAME}
    ...                         ${SUBDIRECTORY NAME}
    ...                         ${FILE WITH SPECIAL CHARS NAME}
    ...                         ${TEST FILE NAME}
    ${listing} =  List Directory  ${REMOTE TEST ROOT NAME}
    Lists Should Be Equal  ${listing}  ${expected}

List Content Using Pattern
    ${expected} =  Create List  ${FILE WITH SPECIAL CHARS NAME}
    ${listing} =  List Directory  ${REMOTE TEST ROOT}  pattern=spec*
    Lists Should Be Equal  ${listing}  ${expected}

List Content Using Current Working Directory
    ${listing} =  List Directory  .
    Should Contain  ${listing}  ${REMOTE TEST ROOT NAME}

List Content Using Symlink As Path
    [Setup]  Execute Command  ln -s ${REMOTE TEST ROOT} symlink
    ${expected} =  Create List
    ...                         ${FILE WITH NEWLINES NAME}
    ...                         ${SUBDIRECTORY NAME}
    ...                         ${FILE WITH SPECIAL CHARS NAME}
    ...                         ${TEST FILE NAME}
    ${listing} =  List Directory  symlink
    Lists Should Be Equal  ${listing}  ${expected}
    [Teardown]  Execute Command  rm -f symlink

List Content Using Non-ASCII Characters In Path
    ${expected} =  Create List  ${FILE WITH NON-ASCII NAME}
    ...                         ${DIRECTORY WITH EMPTY SUBDIRECTORY}
    ${listing} =  List Directory  ${REMOTE TEST ROOT}${/}${SUBDIRECTORY NAME}
    Lists Should Be Equal  ${listing}  ${expected}

List Content With Absolute Paths Using Absolute Path
    ${expected} =  Create List
    ...                 ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    ...                 ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}
    ...                 ${REMOTE TEST ROOT}/${FILE WITH SPECIAL CHARS NAME}
    ...                 ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${listing} =  List Directory  ${REMOTE TEST ROOT}  absolute=True
    Lists Should Be Equal  ${listing}  ${expected}

List Content With Absolute Paths Using Relative Path
    ${expected} =  Create List
    ...                 ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    ...                 ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}
    ...                 ${REMOTE TEST ROOT}/${FILE WITH SPECIAL CHARS NAME}
    ...                 ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${listing} =  List Directory  ${REMOTE TEST ROOT NAME}  absolute=True
    Lists Should Be Equal  ${listing}  ${EXPECTED}

List Content With Absolute Paths Using Pattern
    ${expected} =  Create List
    ...                 ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    ...                 ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${listing} =  List Directory  ${REMOTE TEST ROOT}  pattern=?est*  absolute=True
    Lists Should Be Equal  ${listing}  ${expected}

List Content With Absolute Paths Using Current Working Directory
    ${listing} =  List Directory  .  absolute=True
    Should Contain  ${listing}  ${REMOTE TEST ROOT}

List Content With Absolute Paths Using Symlink As Path
    [Setup]  Execute Command  ln -s ${REMOTE TEST ROOT} symlink
    ${expected} =  Create List
    ...                 ${REMOTE TEST ROOT}/${FILE WITH NEWLINES NAME}
    ...                 ${REMOTE TEST ROOT}/${SUBDIRECTORY NAME}
    ...                 ${REMOTE TEST ROOT}/${FILE WITH SPECIAL CHARS NAME}
    ...                 ${REMOTE TEST ROOT}/${TEST FILE NAME}
    ${listing} =  List Directory  symlink   absolute=True
    Lists Should Be Equal  ${listing}  ${expected}
    [Teardown]  Execute Command  rm -f symlink

List Content Should Fail When Source Path Not Exists
    ${target} =  Set Variable  not_exists
    Run Keyword And Expect Error  There was no directory matching '${target}'.
    ...                           List Directory  ${target}
