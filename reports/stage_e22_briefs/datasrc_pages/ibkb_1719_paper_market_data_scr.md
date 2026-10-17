FAQ: Market data considerations for the paper trading account

Browse FAQs
===========

##### Categories

Common Questions

Account Management & Services

Funding & Asset Transfers

Accounts & Applications

Security & Account Protection

Taxes & Tax Forms

Trading & Margin

‌Ask a question. Don't type any personal information.

AI-Assisted Search Disclosure

Market data considerations for the paper trading account
--------------------------------------------------------

Account Management & Services/

Market Data & Research/

Market Data Configuration

As a licensed distributor of exchange market data, we are obligated to respect constraints imposed by the exchanges which serve to govern the dissemination and/or retransmission of this data.

As a general rule, within a given account, the real user can activate and maintain its own set of market data subscriptions. The paper user, by design, does not have a set of market data subscription on its own but can be configured in one of the following ways:

1. The paper user can be set to share2 the live market data subscriptions of the real user:

* In this scenario, if the real and paper trading sessions are running simultaneously, they must reside on the same device in order for the paper to receive live market data. If this is not the case, the real trading session will be still afforded the real-time market data but the paper trading session will not receive any data3 . Please see the section Case 1 below for details.

2. The paper user can be set NOT to share2 the live market data subscriptions of the real user:

* In this scenario, the real and paper trading sessions are independent, in respect of market data flows. Hence, they can run simultaneously on the same or on different devices and the paper user will receive delayed data, as available. Please see the section Case 1 below for details.

3. In case the account possess multiple real users, the paper user can be set to share2 the live market data subscriptions of a chosen one.

* Clients who wish to run real and paper sessions simultaneously and on different devices (e.g., stand-alone PC, smart phone, tablet), may create an additional real user for their account, as explained here: [Adding a second user for an individual account holder](https://ibkrguides.com/clientportal/uar/addingauser.htm). While this approach will result in additional fees for any paid market data subscriptions elected, it will allow maintaining different subscription sets. In this scenario, the client will be able to select2 which real user will share his subscriptions with the paper user, allowing the other real user and the paper trading sessions to run simultaneously on different devices. Please see the section Case 2 below for details.

**Example Cases**

**Case 1**

**Account users:** 1 real user + 1 paper user

**REAL\_USER** is subscribed to live market data

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Location of real\_user session | Location of paper\_user session | Sharing of live market data between real\_user and paper\_user is active? | Type of market data received by real\_user | Type of market data received by paper\_user |
| DEVICE1 | DEVICE2 | YES | LIVE | No Data |
| DEVICE1 | DEVICE1 | YES | LIVE | Live |
| DEVICE1 | DEVICE2 | NO | LIVE | Delayed |
| DEVICE1 | DEVICE1 | NO | LIVE | Delayed |
| USER NOT LOGGED IN | DEVICE1 | YES | N/A | Live |
| USER NOT LOGGED IN | DEVICE1 | NO | N/A | Delayed |

**CASE 2**

**Account users:** (after the creation of a secondary real user) : 2 real users + 1 paper user

**REAL\_USER1** is subscribed to live market data

**REAL\_USER2** is subscribed to live market data

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Location of real\_user1 session | Location of real\_user2 session | Location of paper\_user session | paper\_user is mirroring the subscriptions of | Type of market data received by real\_user1 | Type of market data received by real\_user2 | Type of market data received by paper\_user |
| USER NOT LOGGED IN | DEVICE1 | DEVICE2 | real\_user1 | N/A | LIVE | LIVE |
| USER NOT LOGGED IN | DEVICE1 | DEVICE1 | real\_user1 | N/A | LIVE | LIVE |
| DEVICE1 | USER NOT LOGGED IN | DEVICE2 | real\_user1 | LIVE | N/A | No Data3 |
| DEVICE1 | USER NOT LOGGED IN | DEVICE1 | real\_user1 | LIVE | N/A | LIVE |
| USER NOT LOGGED IN | DEVICE1 | DEVICE2 | real\_user2 | N/A | LIVE | No Data3 |
| USER NOT LOGGED IN | DEVICE1 | DEVICE1 | real\_user2 | N/A | LIVE | LIVE |
| DEVICE1 | USER NOT LOGGED IN | DEVICE2 | real\_user2 | LIVE | N/A | LIVE |
| DEVICE1 | USER NOT LOGGED IN | DEVICE1 | real\_user2 | LIVE | N/A | LIVE |
| DEVICE1 | DEVICE1 | DEVICE2 | real\_user1 | LIVE | LIVE | No Data3 |
| DEVICE1 | DEVICE1 | DEVICE1 | real\_user1 | LIVE | LIVE | LIVE |
| DEVICE1 | DEVICE2 | DEVICE2 | real\_user2 | LIVE | LIVE | LIVE |
| DEVICE1 | DEVICE1 | DEVICE2 | real\_user1 | LIVE | LIVE | No Data3 |
| DEVICE1 | DEVICE1 | DEVICE2 | Set NOT to mirror | LIVE | LIVE | DELAYED |
| DEVICE1 | DEVICE1 | DEVICE1 | Set NOT to mirror | LIVE | LIVE | DELAYED |
| DEVICE1 | DEVICE2 | DEVICE1 | Set NOT to mirror | LIVE | LIVE | DELAYED |
| DEVICE1 | DEVICE2 | DEVICE2 | Set NOT to mirror | LIVE | LIVE | DELAYED |

**Notes**

**1.Trading Session:** For trading session, we consider a user session successfully established and actively running on any of the following platforms:

* Trader Workstation (TWS)
* Mobile App
* Web Trader
* Client Portal

**2. Market data mirroring and sharing user selection:** On the Client Portal, those functions are present in the section: Settings -> Account Settings -> Configure (gear) icon

**3. No Data:** On the paper session, the trading platform will display a warning message containing: "...production username associated with this paper-trading username is also running on"...

Powered by iBot 2.0

I received an execution in my paper trading account that did not correspond to the market at the time, what happened?

Can multiple users on the same account share the same market data subscription?

What are the historical data limitations of the TWS API?

How do I stream live market data into Excel?

AI-Assisted Search Disclosure
-----------------------------

Our AI assistant, IBot, is powered by Large Language Models (LLMs), and responds to certain client inquiries using FAQs, User Guides, Release Notes, and Knowledge Base found on the IBKR website. It will search these sources – not anything else, including the rest of the internet – and use its proprietary algorithm to provide a response to client questions. IBKR will provide the AI assistant’s response "as is". These responses are not reviewed or edited by IBKR. Although we believe that the AI assistant’s responses are generally accurate, they may not be and IBKR makes no representations or warranties regarding the accuracy of the AI assistant’s responses or how it combines the content of these IBKR’s educational materials to respond to client questions.

This tool uses 3rd party services to provide responses based on your query and IBKR's educational resources. If you enter personally identifiable information (PII) into the search - such as your username, account number or email address - that information could be included in the requests sent to the 3rd party that provides this service. The data will only be used to generate an answer with and will not be saved by the third-party or used for model training of any kind.

For further information on how IBKR protects your personal information please see [IBKR's Privacy Policy](https://gdcdyn.interactivebrokers.com/Universal/servlet/Registration_v2.formSampleView?formdb=2192).

Okay