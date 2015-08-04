Feature: Echo command
  Take an email message with one or more attachments and return it

Scenario: Basic echo command
  Given an email message with a body and attachments
  Then the action should execute
  And make working directories
  And save the message text
  And save the attachments
  And copy the attachments
  And write a response
