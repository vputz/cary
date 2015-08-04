Feature: Cary App
  Parse arbitrary email messages and dispatch them to actions

Scenario Outline: Check allowed emails
  Given A configured app
  And Allowed <patterns> and an <address>
  Then I should check <validity>

  Examples:
  | patterns             | address       | validity |
  | this@that.com, *.net | this@that.com | True     |
  | this@that.com, *.net | that@this.com | False    |
  | this@that.com, *.net | this@that.net | True     |

Scenario Outline: Check help text
  Given A configured app
  And a valid email with invalid command
  Then App should send help text
