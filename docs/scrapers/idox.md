# Idox

## A Visual Walkthrough

Idox make the planning portal for software uses by most local planning authorities in the UK.

This is what the main search form of an Idox planning portal looks like:

### The Main Form

![Idox Main Form](images/idox_main_form.png)

#### The Advanced Search Form

If we click over to the "Advanced" tab, this is what we see:

![Idox Advanced Form](images/idox_main_form_advanced.png)

The URL of the advanced search tab is, in the case of Cambridge:

`https://applications.greatercambridgeplanning.org/online-applications/search.do?action=advanced`

This is the scraper's start URL.

### The Advanced Search Form's Results Page

If we leave the applications button selected, and enter a start and end value for the "Date Validated" field, we get a list of results that looks something like this:

![Idox Search Results](images/idox_main_form_advanced_results.png)

### An Application

If we click on one of those applications, (not on pictured in this case), we get taken to the application's "Details > Summary" tab:

#### The Details > Summary Tab

##### URL

`https://applications.greatercambridgeplanning.org/online-applications/applicationDetails.do?activeTab=summary&keyVal=Q0YSEDDXIK800`

##### Information

- Reference
- Application Received
- Application Validated
- Address
- Proposal
- Status
- Decision
- Decision Issued Date
- Appeal Status
- Appeal Decision

##### Image

![Idox Application Details](images/idox_application_details_summary.png)

#### The Details > Further Information Tab

##### URL

`https://applications.greatercambridgeplanning.org/online-applications/applicationDetails.do?activeTab=details&keyVal=Q0YSEDDXIK800`

##### Information

- Application Type
- Decision
- Expected Decision Level
- Case Officer
- Parish
- Ward
- District Reference
- Applicant Name
- Agent Name
- Agent Company Name
- Agent Address
- Environmental Assessment

##### Image

![Idox Application Details Further Information](images/idox_application_details_further_information.png)

#### The Documents Tab

##### URL

`https://applications.greatercambridgeplanning.org/online-applications/applicationDetails.do?activeTab=documents&keyVal=Q0YSEDDXIK800`

##### Information

For each document, we get:

- Date Published
- Document Type
- Measure
- Drawing Number
- Description

##### Image

![Idox Application Documents](images/idox_application_documents.png)

#### The Map Tab

##### URL

`https://applications.greatercambridgeplanning.org/online-applications/applicationDetails.do?activeTab=map&keyVal=Q0YSEDDXIK800`

##### Image

![Idox Application Map](images/idox_application_map.png)

## The Scraper
