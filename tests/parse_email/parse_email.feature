Feature: Parse email
  Take an email message and extract the FROM, command, etc

Scenario: Parsing an email
  Given the text of an email message
  And that is parsed to a message
  Then I should get the from address
  And I should get the subject
  And I should get the body
  And a list of attachments

