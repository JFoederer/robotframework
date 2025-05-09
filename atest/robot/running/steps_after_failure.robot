*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/steps_after_failure.robot
Resource          atest_resource.robot

*** Test Cases ***
Library keyword after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[2:]}    5
    Check Log Message    ${tc.teardown[0]}    This is run

User keyword after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[1:]}

Non-existing keyword after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[1:]}

Invalid keyword usage after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[1:]}

Assignment after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run     ${tc[1:]}    4
    Check Keyword Data    ${tc[1]}     Not run    assign=\${x}          status=NOT RUN
    Check Keyword Data    ${tc[2]}     Not run    assign=\${x}          status=NOT RUN
    Check Keyword Data    ${tc[3]}     Not run    assign=\${x}, \${y}   status=NOT RUN
    Check Keyword Data    ${tc[4]}     Not run    assign=\${x}, \${y}   status=NOT RUN

IF after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run     ${tc[1:]}
    Should Not Be Run     ${tc[1, 0].body}
    Should Not Be Run     ${tc[1, 1].body}
    Check Keyword Data    ${tc[1, 1, 0]}
    ...    BuiltIn.Fail    assign=\${x}    args=This should not be run    status=NOT RUN

GROUP after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run     ${tc[1:]}
    Should Not Be Run     ${tc[1].body}    2
    Check Keyword Data    ${tc[1, 1]}
    ...    BuiltIn.Fail    assign=\${x}    args=This should not be run    status=NOT RUN

FOR after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run     ${tc[1:]}
    Should Not Be Run     ${tc[1].body}
    Should Not Be Run     ${tc[1, 0].body}    2
    Check Keyword Data    ${tc[1, 0, 1]}
    ...    BuiltIn.Fail    assign=\${x}    args=This should not be run either    status=NOT RUN

TRY after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run     ${tc[1:]}
    Should Not Be Run     ${tc[1].body}    4
    FOR    ${step}    IN    @{tc[1].body}
        Should Not Be Run     ${step.body}
    END

WHILE after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run     ${tc[1:]}           3
    Should Not Be Run     ${tc[1].body}
    Should Not Be Run     ${tc[1, 0].body}    3
    Should Not Be Run     ${tc[2].body}
    Should Not Be Run     ${tc[2, 0].body}    2
    Should Not Be Run     ${tc[3].body}
    Should Not Be Run     ${tc[3, 0].body}    1

RETURN after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run     ${tc[1:]}
    Should Not Be Run     ${tc[0][1:]}        2
    Should Be Equal       ${tc[0, 1].type}    RETURN

BREAK and CONTINUE after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run     ${tc[1:]}           1
    Should Not Be Run     ${tc[0, 0][1:]}     2
    Should Not Be Run     ${tc[1].body}
    Should Not Be Run     ${tc[1, 0].body}    2

Nested control structure after failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[1:]}    2
    Should Be Equal      ${tc[1].type}    FOR
    Should Not Be Run    ${tc[1].body}    1
    Should Be Equal      ${tc[1, 0].type}    ITERATION
    Should Not Be Run    ${tc[1, 0].body}    2
    Should Be Equal      ${tc[1, 0, 0].type}    IF/ELSE ROOT
    Should Not Be Run    ${tc[1, 0, 0].body}    2
    Should Be Equal      ${tc[1, 0, 0, 0].type}    IF
    Should Not Be Run    ${tc[1, 0, 0, 0].body}    2
    Should Be Equal      ${tc[1, 0, 0, 0, 0].type}    FOR
    Should Not Be Run    ${tc[1, 0, 0, 0, 0].body}    1
    Should Be Equal      ${tc[1, 0, 0, 0, 0, 0].type}    ITERATION
    Should Not Be Run    ${tc[1, 0, 0, 0, 0, 0].body}    2
    Should Be Equal      ${tc[1, 0, 0, 0, 0, 0, 0].type}    KEYWORD
    Should Be Equal      ${tc[1, 0, 0, 0, 0, 0, 1].type}    GROUP
    Should Not Be Run    ${tc[1, 0, 0, 0, 0, 0, 1].body}    2
    Should Be Equal      ${tc[1, 0, 0, 0, 0, 0, 1, 0].type}    KEYWORD
    Should Be Equal      ${tc[1, 0, 0, 0, 0, 0, 1, 1].type}    KEYWORD
    Should Be Equal      ${tc[1, 0, 0, 0, 1].type}    KEYWORD
    Should Be Equal      ${tc[1, 0, 0, 1].type}    ELSE
    Should Not Be Run    ${tc[1, 0, 0, 1].body}    2
    Should Be Equal      ${tc[1, 0, 0, 1, 0].type}    WHILE
    Should Not Be Run    ${tc[1, 0, 0, 1, 0].body}    1
    Should Be Equal      ${tc[1, 0, 0, 1, 0, 0].type}    ITERATION
    Should Not Be Run    ${tc[1, 0, 0, 1, 0, 0].body}    2
    Should Be Equal      ${tc[1, 0, 0, 1, 0, 0, 0].type}    KEYWORD
    Should Be Equal      ${tc[1, 0, 0, 1, 0, 0, 1].type}    KEYWORD
    Should Be Equal      ${tc[1, 0, 0, 1, 1].type}    TRY/EXCEPT ROOT
    Should Not Be Run    ${tc[1, 0, 0, 1, 1].body}    2
    Should Be Equal      ${tc[1, 0, 0, 1, 1, 0].type}    TRY
    Should Not Be Run    ${tc[1, 0, 0, 1, 1, 0].body}    1
    Should Be Equal      ${tc[1, 0, 0, 1, 1, 0, 0].type}    KEYWORD
    Should Be Equal      ${tc[1, 0, 0, 1, 1, 1].type}    EXCEPT
    Should Not Be Run    ${tc[1, 0, 0, 1, 1, 1].body}    1
    Should Be Equal      ${tc[1, 0, 0, 1, 1, 1, 0].type}    BREAK
    Should Be Equal      ${tc[1, 0, 1].type}    KEYWORD
    Should Be Equal      ${tc[2].type}    KEYWORD

Failure in user keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[1:]}
    Should Not Be Run    ${tc[0][1:]}    2

Failure in IF branch
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[0, 0][1:]}
    Should Not Be Run    ${tc[0, 1].body}
    Should Not Be Run    ${tc[1:]}

Failure in ELSE IF branch
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[0, 0].body}
    Should Not Be Run    ${tc[0, 1][1:]}
    Should Not Be Run    ${tc[0, 2].body}
    Should Not Be Run    ${tc[1:]}

Failure in ELSE branch
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[0, 0].body}
    Should Not Be Run    ${tc[0, 1][1:]}
    Should Not Be Run    ${tc[1:]}

Failure in GROUP
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[0, 0][1:]}
    Should Not Be Run    ${tc[0][1:]}    2
    Should Not Be Run    ${tc[0, 2].body}
    Should Not Be Run    ${tc[1:]}

Failure in FOR iteration
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Not Be Run    ${tc[1:]}
    Length Should Be     ${tc[0].body}    1
    Should Not Be Run    ${tc[0, 0][1:]}

*** Keywords ***
Should Not Be Run
    [Arguments]    ${steps}    ${expected count}=1
    FOR    ${step}    IN    @{steps}
        Should Be Equal    ${step.status}    NOT RUN
    END
    Length Should Be    ${steps}    ${expected count}
