# Notice: ownership and scope

**ServiceNow®, the Agent Client Collector (ACC) agent, the MID Server, the Agent Client Collector Framework and
the Visibility content are products of ServiceNow, Inc. and remain the property of ServiceNow.** They are proprietary
software, not open source, and nothing in this repository changes that.

This repository holds only **acctest**, an independent test harness that drives a ServiceNow agent release through a
set of checks and writes a report. It is published **for use and information only**:

* It contains **no ServiceNow software**. Agent packages are downloaded at run time from your own ServiceNow instance
  with your own credentials into `dist/`, which is never committed. Plugin content, check definitions and the install
  script come from your instance at run time as well.
* It **does not modify** the agent, the MID Server or any ServiceNow content. It installs the agent exactly as
  ServiceNow ships it and observes what happens.
* Findings about the agent or about ServiceNow content described here (for example the CRLF plugin files or the
  `basic_inventory` module in Visibility content 2.1.1) are observations from a lab. **Any change to the agent, its
  content or its behaviour is ServiceNow's to make - contact ServiceNow Support (a HI / Now Support case) rather than
  patching ServiceNow files yourself.** Modified ServiceNow files are unsupported.
* Nothing here is endorsed by, affiliated with or reviewed by ServiceNow. ServiceNow and the ServiceNow logo are
  trademarks of ServiceNow, Inc.; other names belong to their owners.

The harness itself is shared without warranty of any kind, for reference and personal use. See `LICENSE`.
