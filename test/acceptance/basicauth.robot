*** Settings ***
Resource          resource.txt

*** Test Cases ***
Http Authentication
    Create Soap Client    ${TEST WSDL URL}
    Set Location    ${SECURE TEST URL}
    Run Keyword And Expect Error    (401, u'Authentication Required')    Call Soap Method    theAnswer
    Set Http Authentication    bob    bob    STANDARD
    ${answer}    Call Soap Method    theAnswer
    Should Be Equal    ${answer}    ${42}
    Create Soap Client    ${TEST WSDL URL}
    Set Http Authentication    bob    foo    ALWAYS_send
    ${sum}    Call Soap Method    theAnswer
    ${request}    Get Sent Request
    # auth not needed, but should have been sent anyways
    Should Be Equal As Strings    ${request.headers['Authorization']}    Basic Ym9iOmZvbw==

Secured WSDL
    Run Keyword And Expect Error    *401*    Create Soap Client    ${SECURE TEST WSDL URL}    # sanity check
    Create Soap Client    ${SECURE TEST WSDL URL}    username=beth    password=beth
    ${answer}    Call Soap Method    theAnswer
    Should Be Equal    ${answer}    ${42}

Unsecure WSDL With Secured Import
    [Documentation]    To test that the transport is used on imports, use a WSDL that does not require authentication that imports a document that does require authentication.
    Create Soap Client    ${WSDL DIR}/TestServices_secured_import.wsdl    username=beth    password=beth
    ${answer}    Call Soap Method    theAnswer
    Should Be Equal    ${answer}    ${42}

Bad Authentication Type
    Run Keyword And Expect Error    ValueError: 'bad' is not a supported authentication type.    Create Soap Client    ${TEST WSDL URL}    username=bob    password=foo    auth_type=bad
    Create Soap Client    ${TEST WSDL URL}
    Run Keyword And Expect Error    ValueError: 'bad' is not a supported authentication type.    Set Http Authentication    bob    foo    bad
