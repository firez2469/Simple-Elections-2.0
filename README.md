# Simple-Elections-2.0
A repo for the updated SimpleElections bot. Open source for self-hosting.

## Dependencies
- [Discord.py](https://pypi.org/project/discord.py/)
- [MatPlotLib](https://pypi.org/project/matplotlib/)


## Getting Started
### Setting Up Permissions
Run `/admin add_admin_role [YOUR DISCORD ROLE]` to ensure at least one role has admin by the bot. This command reqires the discord admin permissions to run. You can verify this has worked by running `/admin roles`. If the role is in the embed message, then you should have the correct permission. 

### Creating an Election
Run `/election create [ELECTION NAME] [DATE]` to create a new election. Feel free to replace `[ELECTION NAME]` with your own. `[DATE]` can be anything to describe when it will happen.

If you then run `/election list`, you will see the election listed. Its permissions by default disable voting and candidacy. It also lists the ID for the given election. You can use filters if you wish, but these are optional.

Run `/election add_candidate [ELECTION ID] [USER]`. To add another person to an election. This can only be run by a person with an elections admin role.

### Enabling Election Permissions

In order to allow people to join an election run `/election toggle_candidacy [election ID]`. A messege will confirm the new permission. You can also verify the update via `/election list` or `/election get [election ID]`.

Once the election allows candidates to run, execute `/election join [ELECTION ID/ELECTION NAME]` to join an election. Discord will provide the option of choosing by name or id. You can view all candidates currently in an election via `/election get [ELECTION ID/ELECTION NAME]`.

In order to allow people to vote in an election. Run `/election toggle_voting [election ID]`. A messege will confirm the new permissions. You can alos verify the update via `/election list` or `/election get [election ID]`.

### Voting

To vote in an election that has the permission enabled run: `/election vote [ELECTION ID/ELECTION NAME]`. The discord bot will then send the user a direct message on discord with a dropdown for voting. Once selected the vote is cast. You can only vote once for an election.

*NOTE: THIS FEATURE STILL IS BEING DEVELOPED SO THAT VOTES CAN BE OVERWRITTEN.*

### Viewing Results
Run `/election results [Election ID]` as an admin to view the results of an election.

Now you know the basics of using this bot. Further details on commands are listed below or on the discord slash commands menu.

## Commands
This discord bot exclusively uses the discord slash commands functionality. 

`Discord Admin Required`: States that the admin permission on a discord server is required.<br>
`Bot Admin Required`: States that a role which has been set as an admin role is required.

These permissions may be necessary to execute the following commands.

|Command Header|Command Name|Decription|Discord Admin Required|Bot Admin Required|
|--------------|------------|----------|---|---|
|Election|`create`|Creates an election of a given name and date.|❌|✅|
|Election|`delete`|Deletes an election of a given id.|❌|✅|
|Election|`list`|Lists out all elections. Filters may be applied by the user.|❌|❌|
|Election|`get`   |Gets name,date,id,candidacy,voting, and candidates for a specific election.|❌|❌|
|Election|`vote`|Vote for a specific election. A ballot is then DM'ed to the user to vote. (if allowed)|❌|❌|
|Election|`join`|Candidate yourself for a specific election. (if allowed)|❌|❌|
|Election|`leave`|Un-candidate yourself for a specific election. (if allowed)|❌|❌|
|Election|`results`|Gets the results of an election.|✅|❌|
|Admin|`add_admin_role`|Sets a discord role as a Admin for the bot.|✅|❌|
|Admin|`remove_admin_role`|Removes a discord role as a Admin for the bot.|✅|❌|
|Admin|`roles`|Gets all discord roles with election admin privledges.|✅|❌|
|Admin|`add_candidate`|Add a candidate to an election.|❌|✅|
|Admin|`remove_candidate`|Remove a candidate from an election.|❌|✅|
|Admin|`toggle_candidacy`|Enable/disable the ability for user to candidate for a specific election.|❌|✅|
|Admin|`toggle_voting`|Enable/disable the ability for a user to vote in a specific election.|❌|✅|
|Config|`add_candidacy_roles`|All members with the given role may run as candidates.|✅|❌|
|Config|`remove_candidacy_roles`|Removes permissions from a role to candidate for an election.|✅|❌|
|Config|`candidacy_roles`|Lists all roles permitted to candidate for an election.|✅|❌|
|Config|`toggle_candidacy_perms`|Toggles whether or not candidacy permissions are restricted.|✅|❌|
|Config|`add_voting_role`|All members with the given role may vote in elections.|✅|❌|
|Config|`remove_voting_role`|Removes the permission to vote from a given role.|✅|❌|
|Config|`voting_roles`|List all roles that can vote.|❌|❌|
|Config|`toggle_voting_perms`|Toggles whether or not voting permissions are restricted.|✅|❌|
|Config|`election`|Configue an election setting permissions manually.|❌|✅|
|Results|`graph`|Export the results of an election as a graph|❌|✅|
|Results|`export`|Export the results of an election as a csv|❌|✅|

## Installation
Clone this repository for self-hosting.

## Backend Files
- Savefile autogenerated on start if missing. Saved in `savefile.json`.
- Graphs exported to `election_results_pie_chart.png` and is overwritten every send.
- CSV files stored under `election_results.csv` and is overwritten every send.



## License
[Mit License](./LICENSE)

Developed by Marco Sebastian Hampel, 2024.
