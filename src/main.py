import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands, SelectMenu, SelectOption,ui
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from typing import Optional
import datetime

import savefile

load_dotenv()

# Loads the token from the .env file
TOKEN = os.getenv('DISCORD_TOKEN')

# Enables all discord intents.
intents = discord.Intents.all()

# Creates a bot object with the specified command prefix and intents.
bot = commands.Bot(command_prefix="!", intents=intents)

# Creates a group of commands for the bot.
admin_commands = app_commands.Group(name="admin",description="Admin commands")
election_commands = app_commands.Group(name="election",description="Election commands")
config_commands = app_commands.Group(name="config",description="Configuration commands")
results_commands = app_commands.Group(name="results",description="Results commands")

# Create a new Election Command.
@election_commands.command(name="create",description="Create a new election",extras={"date":"The date of the election"})
@app_commands.describe(name="Name of the election",date="Date of the election",params="Optional parameters")
async def create(ctx,name:str,date:str, params: Optional[str] = None):
    savefile.load()
    # check if the user has the admin role
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]

    # check if the user has the admin role
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to create an election.")
    else:
        # create the election
        filedata = savefile.setup_base_election_savefile(savefile.ELECTIONS_COUNTER,name,ctx.user.id)
        filedata["date"]=date
        savefile.ELECTIONS_COUNTER+=1
        savefile.save_file[str(ctx.guild.id)]["elections"].append(filedata)
        await ctx.response.send_message(f"Created election {name} on {date}")
    # save the file
    savefile.save()

# Delete a new election command.
@election_commands.command(name="delete",description="Delete an election")
@app_commands.describe(election_id="The id of the election to delete")
async def delete(ctx,election_id:int):
    # load the savefile
    savefile.load()
    # check if the user has the admin role
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]

    # check if the user has the admin role
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to delete an election.")
    else:
        # get the elections
        elections = savefile.save_file[str(ctx.guild.id)]["elections"]
        for election in elections:
            if election["id"] == election_id:
                elections.remove(election)
                await ctx.response.send_message(f"Deleted election {election_id}")
                savefile.save()
                return
        await ctx.response.send_message(f"Election {election_id} not found.")

# Get details of an election command.
@election_commands.command(name="get",description="Get details of an election")
@app_commands.describe(election_id="The id of the election to get details of")
async def get(ctx,election_name:str=None, election_id:int=-1):
    savefile.load()
    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    for election in elections:
        if election["id"] == election_id or election["name"] == election_name:
            embed = discord.Embed(title=f"Election: **{election['name']}**", description=f"Details of election {election['id']}", color=discord.Color.blue())
            embed.add_field(name="Date", value=election["date"], inline=False)
            embed.add_field(name="Candidacy Enabled", value=election["candidacy_enabled"], inline=False)
            embed.add_field(name="Voting Enabled", value=election["voting_enabled"], inline=False)
            # add the candidates
            candidates = ""
            for candidate in election["candidates"]:
                candidates+=f"{discord.utils.get(ctx.guild.members,id=candidate)}\n"
            embed.add_field(name="Candidates", value=candidates, inline=False)
            await ctx.response.send_message(embed=embed)
            return
    await ctx.response.send_message(f"Election {election_id} not found.")

# Update an election command.
@admin_commands.command(name="add_admin_role", description="Assigns manage guild permissions to a role")
@has_permissions(administrator=True)
async def add_admin_role(ctx, role: discord.Role):
    savefile.load()
    savefile.save_file[str(ctx.guild.id)]["admin_roles"].append(role.id)
    savefile.save()
    await ctx.response.send_message(f"Added {role} to the list of admin roles.")

# Remove an election command.
@admin_commands.command(name="remove_admin_role", description="Removes manage guild permissions from a role")
@has_permissions(administrator=True)
async def remove_admin_role(ctx, role: discord.Role):
    savefile.load()
    savefile.save_file[str(ctx.guild.id)]["admin_roles"].remove(role.id)
    savefile.save()
    await ctx.response.send_message(f"Removed {role} from the list of admin roles.")

# Get the results of an election command.
@election_commands.command(name="results", description="Get the results of an election")
@app_commands.describe(election_id="The id of the election to get results of")
async def results(ctx, election_id:int):
    savefile.load()

    # check if has admin permissions to run this command
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to view the results of an election.")
        return

    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    for election in elections:
        if election["id"] == election_id:
            embed = discord.Embed(title=f"Results for {election['name']}", description=f"Results of election {election['id']}", color=discord.Color.blue())
            # get the candidates
            candidates = election["candidates"]
            for candidate in candidates:
                votes = 0
                for voter in election["voters"]:
                    if voter["candidate"] == candidate:
                        votes+=1
                embed.add_field(name=f"{discord.utils.get(ctx.guild.members,id=candidate)}", value=f"Votes: {votes}", inline=False)
            await ctx.response.send_message(embed=embed)
            return
    await ctx.response.send_message(f"Election {election_id} not found.")


# List all roles with admin privileges command.
@admin_commands.command(name="roles", description="Lists all admin roles")
async def roles(ctx):
    savefile.load()
    admin_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]
    embed = discord.Embed(title="Election Admin Roles", description="List of all roles that can create/update/delete elections", color=discord.Color.blue())
    for role in admin_roles:
        # given the role-id role, get the role object
        role = discord.utils.get(ctx.guild.roles, id=role)
        embed.add_field(name=role, value="", inline=False)
    await ctx.response.send_message(embed=embed,ephemeral=True)

# Add a role that is allowed to candidate.
@config_commands.command(name="add_candidacy_role", description="Assigns permissions to a role to add candidates to an election")
@has_permissions(administrator=True)
async def add_candidacy_role(ctx, role: discord.Role):
    savefile.load()
    savefile.save_file[str(ctx.guild.id)]["candidacy_roles"].append(role.id)
    savefile.save()
    await ctx.response.send_message(f"Added {role} to the list of candidacy roles.")

# Remove a role that is allowed to candidate.
@config_commands.command(name="remove_candidacy_role", description="Removes permissions from a role to add candidates to an election")
@has_permissions(administrator=True)
async def remove_candidacy_role(ctx, role: discord.Role):
    savefile.load()
    savefile.save_file[str(ctx.guild.id)]["candidacy_roles"].remove(role.id)
    savefile.save()
    await ctx.response.send_message(f"Removed {role} from the list of candidacy roles.")

# List all roles with candidacy privileges command.
@config_commands.command(name="candidacy_roles", description="Lists all candidacy roles")
async def candidacy_roles(ctx):
    savefile.load()
    candidacy_roles = savefile.save_file[str(ctx.guild.id)]["candidacy_roles"]
    embed = discord.Embed(title="Candidacy Roles", description="List of all roles that can add candidates to an election", color=discord.Color.blue())
    for role in candidacy_roles:
        # given the role-id role, get the role object
        role = discord.utils.get(ctx.guild.roles, id=role)
        embed.add_field(name=role, value="", inline=False)
    await ctx.response.send_message(embed=embed,ephemeral=True)

# Toggle candidacy permissions command. When off all roles can candidate.
@config_commands.command(name="toggle_candidacy_perms", description="Toggle permissions for roles to add candidates to an election")
@has_permissions(administrator=True)
async def toggle_candidacy_perms(ctx):
    savefile.load()
    savefile.save_file[str(ctx.guild.id)]["candidacy_perms_enabled"] = not savefile.save_file[str(ctx.guild.id)]["candidacy_perms_enabled"]
    savefile.save()
    if savefile.save_file[str(ctx.guild.id)]["candidacy_perms_enabled"]:
        await ctx.response.send_message("Enabled candidacy permissions.")
    else:
        await ctx.response.send_message("Disabled candidacy permissions.")

# Add a role that is allowed to vote.
@config_commands.command(name="add_voting_role", description="Assigns permissions to a role to vote in an election")
@has_permissions(administrator=True)
async def add_voting_role(ctx, role: discord.Role):
    savefile.load()
    savefile.save_file[str(ctx.guild.id)]["voting_roles"].append(role.id)
    savefile.save()
    await ctx.response.send_message(f"Added {role} to the list of voting roles.")

# Remove a role that is allowed to vote.
@config_commands.command(name="remove_voting_role", description="Removes permissions from a role to vote in an election")
@has_permissions(administrator=True)
async def remove_voting_role(ctx, role: discord.Role):
    savefile.load()
    savefile.save_file[str(ctx.guild.id)]["voting_roles"].remove(role.id)
    savefile.save()
    await ctx.response.send_message(f"Removed {role} from the list of voting roles.")

# List all roles with voting privileges command.
@config_commands.command(name="voting_roles", description="Lists all voting roles")
async def voting_roles(ctx):
    savefile.load()
    voting_roles = savefile.save_file[str(ctx.guild.id)]["voting_roles"]
    embed = discord.Embed(title="Voting Roles", description="List of all roles that can vote in an election", color=discord.Color.blue())
    for role in voting_roles:
        # given the role-id role, get the role object
        role = discord.utils.get(ctx.guild.roles, id=role)
        embed.add_field(name=role, value="", inline=False)
    await ctx.response.send_message(embed=embed,ephemeral=True)

# Toggle voting permissions command. When off all roles can vote.
@config_commands.command(name="toggle_voting_perms", description="Toggle permissions for roles to vote in an election")
@has_permissions(administrator=True)
async def toggle_voting_perms(ctx):
    savefile.load()
    savefile.save_file[str(ctx.guild.id)]["voting_perms_enabled"] = not savefile.save_file[str(ctx.guild.id)]["voting_perms_enabled"]
    savefile.save()
    if savefile.save_file[str(ctx.guild.id)]["voting_perms_enabled"]:
        await ctx.response.send_message("Enabled voting permissions.")
    else:
        await ctx.response.send_message("Disabled voting permissions.")

# List all elections command.
@election_commands.command(name="list", description="Get the list of elections")
async def list(ctx,open: Optional[bool] = None, candidacy: Optional[bool] = None):
    savefile.load()
    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    embed = discord.Embed(title="All Elections", description=f"List of all elections with filters\n*Open:*{open}\n*Candidacy:*{candidacy}", color=discord.Color.blue())
    for election in elections:
        election_text = f"Id:{election['id']}\nDate:{election['date']}\n\tCandidacy Open:{election['candidacy_enabled']}\n\tVoting Open:{election['voting_enabled']}"
        if open != None:
            if str(open) != str(election['voting_enabled']):
                continue
        if candidacy != None:
            if str(candidacy) != str(election['candidacy_enabled']):
                continue
        
        embed.add_field(name=f"**{election['name']}**", value=election_text, inline=False)
        
    await ctx.response.send_message(embed=embed,ephemeral=False)

# Configure an election command.
@config_commands.command(name="election", description="Configure an election")
@app_commands.describe(election_id="The id of the election to configure", name="The name of the election", date="The date of the election", candidacy="Enable candidacy", voting="Enable voting")
async def election(ctx, election_id: int, name: Optional[str] = None, date: Optional[str] = None, candidacy: Optional[bool] = None, voting: Optional[bool] = None):
    savefile.load()
    # first check if the user has permissions from admin_roles
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to configure an election.")
        return

    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    for election in elections:
        if election["id"] == election_id:
            if name != None:
                election["name"] = name
            if date != None:
                election["date"] = date
            if candidacy != None:
                election["candidacy_enabled"] = candidacy
            if voting != None:
                election["voting_enabled"] = voting
            await ctx.response.send_message(f"Updated election {election_id}")
            savefile.save()
            return
    await ctx.response.send_message(f"Election {election_id} not found.")

# Add a candidate to an election command.
@admin_commands.command(name="add_candidate", description="Add a candidate to an election")
@app_commands.describe(election_id="The id of the election to add the candidate to", candidate="The candidate to add")
async def add_candidate(ctx, election_id: int, candidate: discord.Member):
    savefile.load()
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to add a candidate.")
        return

    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    for election in elections:
        if election["id"] == election_id:
            election["candidates"].append(candidate.id)
            await ctx.response.send_message(f"Added {candidate} to election {election_id}")
            savefile.save()
            return
    await ctx.response.send_message(f"Election {election_id} not found.")

# Remove a candidate from an election command.
@admin_commands.command(name="remove_candidate", description="Remove a candidate from an election")
@app_commands.describe(election_id="The id of the election to remove the candidate from", candidate="The candidate to remove")
async def remove_candidate(ctx, election_id: int, candidate: discord.Member):
    savefile.load()
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to remove a candidate.")
        return

    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    for election in elections:
        if election["id"] == election_id:
            election["candidates"].remove(candidate.id)
            await ctx.response.send_message(f"Removed {candidate} from election {election_id}")
            savefile.save()
            return
    await ctx.response.send_message(f"Election {election_id} not found.")

# Toggle candidacy for an election command.
@admin_commands.command(name="toggle_candidacy", description="Toggle candidacy for an election")
@app_commands.describe(election_id="The id of the election to toggle candidacy")
async def toggle_candidacy(ctx, election_id: int):
    savefile.load()
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to toggle candidacy.")
        return

    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    for election in elections:
        if election["id"] == election_id:
            election["candidacy_enabled"] = not election["candidacy_enabled"]
            if election["candidacy_enabled"]:
                await ctx.response.send_message(f"Enabled candidacy for election {election_id}")
            else:
                await ctx.response.send_message(f"Disabled candidacy for election {election_id}")
            savefile.save()
            return
    await ctx.response.send_message(f"Election {election_id} not found.")

# Toggle voting for an election command.
@admin_commands.command(name="toggle_voting", description="Toggle voting for an election")
@app_commands.describe(election_id="The id of the election to toggle voting")
async def toggle_voting(ctx, election_id: int):
    savefile.load()
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to toggle voting.")
        return

    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    for election in elections:
        if election["id"] == election_id:
            election["voting_enabled"] = not election["voting_enabled"]
            if election["voting_enabled"]:
                await ctx.response.send_message(f"Enabled voting for election {election_id}")
            else:
                await ctx.response.send_message(f"Disabled voting for election {election_id}")
            savefile.save()
            return
    await ctx.response.send_message(f"Election {election_id} not found.")

# Create a select menu for voting.
class CandidateSelect(ui.Select):
    def __init__(self, candidates, server_id:str=0, election_id:int=0):
        self.server_id = server_id
        self.election_id = election_id
        # The options are created from the list of candidates
        options = [discord.SelectOption(label=candidate, value=candidate) for candidate in candidates]
        # Initialize the select menu with these options and a placeholder
        super().__init__(placeholder="Select a candidate", options=options, custom_id="candidate_select_menu")
    
    # This method is called when the user selects an option
    async def callback(self, interaction: discord.Interaction):
        # given the name find the user by name using discord.py
        name = str(self.values[0])
        # given server_id (which is the guild id get the guild object)
        guild = discord.utils.get(bot.guilds,id=int(self.server_id))
        user = discord.utils.get(guild.members,name=name)
        savefile.load()
        elections = savefile.save_file[str(self.server_id)]["elections"]
        index = 0
        for election in elections:
            if election["id"] == self.election_id:
                break
            index+=1
        savefile.save_file[str(self.server_id)]["elections"][index]["voters"].append({
            "user":interaction.user.id,
            "election":self.election_id,
            "voted?":True,
            "candidate":user.id,
            "date":str(datetime.datetime.now()),
        })
        savefile.save()

        # This is called when a user selects an option
        await interaction.response.send_message(f"You voted for {self.values[0]}!")

# Create a view for the election
class ElectionView(ui.View):
    def __init__(self, candidates,server_id, election_id):
        super().__init__()
        self.candidates = candidates
        self.add_item(CandidateSelect(candidates,server_id=server_id,election_id=election_id))


# Vote for a candidate in an election command.
@election_commands.command(name="vote", description="Vote for a candidate in an election")
async def vote(ctx, election_name:str= None, election_id:int= 0):
    savefile.load()

    if not savefile.save_file[str(ctx.guild.id)]["elections"][election_id]["voting_enabled"]:
        await ctx.response.send_message("Voting is not yet enabled for this election.")
        return

    # check if the user has the voting role
    if savefile.save_file[str(ctx.guild.id)]["voting_perms_enabled"]:
        permissable_roles = savefile.save_file[str(ctx.guild.id)]["voting_roles"]
        if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
            await ctx.response.send_message("You do not have permission to vote.")
            return
    # check if the user has already voted
    for voter in savefile.save_file[str(ctx.guild.id)]["elections"][election_id]["voters"]:
        if voter["user"] == ctx.user.id:
            await ctx.response.send_message("You have already voted.")
            return
    # iterate over candidates for listing in the embed message.
    candidates = ""
    _candidates = []
    for candidate in savefile.save_file[str(ctx.guild.id)]["elections"][election_id]["candidates"]:
        candidates+=f"{discord.utils.get(ctx.guild.members,id=candidate)}\n"
        _candidates.append(discord.utils.get(ctx.guild.members,id=candidate).name)
    embed = discord.Embed(title=f"Vote for {savefile.save_file[str(ctx.guild.id)]['elections'][election_id]['name']}", description=f"Vote for a candidate in the election", color=discord.Color.blue())
    embed.add_field(name="Candidates", value=candidates, inline=False)

    # if there are duplicates add numbers behind them
    for candidate in _candidates:
        if _candidates.count(candidate) > 1:
            _candidates[_candidates.index(candidate)] = f"{candidate} {_candidates.count(candidate)}"

    # create the view and send to dms/server.
    view = ElectionView(_candidates,str(ctx.guild.id),election_id)
    await ctx.user.send(embed=embed, view=view)
    await ctx.response.send_message("Check your DMs for the ballot.")

# Join an election command.
@election_commands.command(name="join", description="Run as a candidate in an election")
async def join(ctx, election_name:str=None,election_id:int=-1):
    savefile.load()

    if election_name != None and election_id == -1:
        for election in savefile.save_file[str(ctx.guild.id)]["elections"]:
            if election["name"] == election_name:
                election_id = election["id"]
                break
    if not savefile.save_file[str(ctx.guild.id)]["elections"][election_id]["candidacy_enabled"]:
        permissable_roles = savefile.save_file[str(ctx.guild.id)]["candidacy_roles"]
        if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
            await ctx.response.send_message("You do not have permission to run for a position in this election.")
            return
        else:
            await ctx.response.send_message("This election does not allow candidacy management.")
            return
    for voter in savefile.save_file[str(ctx.guild.id)]["elections"][election_id]["candidates"]:
        if voter == ctx.user.id:
            await ctx.response.send_message("You are already a candidate.")
            return
    savefile.save_file[str(ctx.guild.id)]["elections"][election_id]["candidates"].append(ctx.user.id)
    savefile.save()
    await ctx.response.send_message("You are now a candidate in this election.")

# Leave an election command.
@election_commands.command(name="leave", description="Leave as a candidate in an election")
async def leave(ctx, election_name:str=None,election_id:int=-1):
    savefile.load()

    if election_name != None and election_id == -1:
        for election in savefile.save_file[str(ctx.guild.id)]["elections"]:
            if election["name"] == election_name:
                election_id = election["id"]
                break
    if not savefile.save_file[str(ctx.guild.id)]["elections"][election_id]["candidacy_enabled"]:
        permissable_roles = savefile.save_file[str(ctx.guild.id)]["candidacy_roles"]
        if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
            await ctx.response.send_message("You do not have permission to manage positions in this election.")
            return
        else:
            await ctx.response.send_message("This election does not allow candidacy management.")
            return
    for voter in savefile.save_file[str(ctx.guild.id)]["elections"][election_id]["candidates"]:
        if voter == ctx.user.id:
            savefile.save_file[str(ctx.guild.id)]["elections"][election_id]["candidates"].remove(ctx.user.id)
            savefile.save()
            await ctx.response.send_message("You are no longer a candidate in this election.")
            return
    await ctx.response.send_message("You are not a candidate in this election.")


# Get the results of an election as a graph command.
@results_commands.command(name="graph", description="Get the results of an election")
@app_commands.describe(election_id="The id of the election to get results of")
async def graph(ctx, election_id: int):
    savefile.load()

    # check if has admin permissions to run this command
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to view the results of an election.")
        return

    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    for election in elections:
        if election["id"] == election_id:
            # Get the candidate names and their vote counts
            candidates = [discord.utils.get(ctx.guild.members, id=candidate_id).name for candidate_id in election["candidates"]]
            votes = [0] * len(candidates)
            for voter in election["voters"]:
                if voter["candidate"] in election["candidates"]:
                    votes[election["candidates"].index(voter["candidate"])] += 1

            # Create a pie chart
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.pie(votes, labels=candidates, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title('Election Results')

            # Save the plot as a PNG file
            file_path = 'election_results_pie_chart.png'
            plt.savefig(file_path)
            plt.close()

            # Send the image in a Discord message
            with open(file_path, 'rb') as f:
                picture = discord.File(f)
                await ctx.response.send_message("Here are the election results:", file=picture)
            f.close()
            return

    await ctx.response.send_message(f"Election {election_id} not found.")

# Export the results of an election as a csv command.
@results_commands.command(name="export",description="Export the results of an election")
@app_commands.describe(election_id="The id of the election to export results of")
async def export(ctx, election_id:int):
    savefile.load()

    # check if has admin permissions to run this command
    permissable_roles = savefile.save_file[str(ctx.guild.id)]["admin_roles"]
    if bool(len(set(permissable_roles).intersection(set([role.id for role in ctx.user.roles]))) == 0):
        await ctx.response.send_message("You do not have permission to view the results of an election.")
        return

    elections = savefile.save_file[str(ctx.guild.id)]["elections"]
    for election in elections:
        if election["id"] == election_id:
            # Get the candidate names and their vote counts
            candidates = [discord.utils.get(ctx.guild.members, id=candidate_id).name for candidate_id in election["candidates"]]
            votes = [0] * len(candidates)
            for voter in election["voters"]:
                if voter["candidate"] in election["candidates"]:
                    votes[election["candidates"].index(voter["candidate"])] += 1

            # Write the results to a CSV file
            file_path = 'election_results.csv'
            with open(file_path, 'w') as f:
                f.write('Candidate,Votes\n')
                for candidate, vote in zip(candidates, votes):
                    f.write(f'{candidate},{vote}\n')

            # Send the CSV file in a Discord message
            with open(file_path, 'rb') as f:
                file = discord.File(f)
                await ctx.response.send_message("Here are the election results:", file=file)
            f.close()
            return

    await ctx.response.send_message(f"Election {election_id} not found.")

# helper function to initialize guild data
def __initialize_guild(guild_id:str, guild_name:str):
    if str(guild_id) not in savefile.save_file:
        print(f"Updated guild data for {guild_name}")
        savefile.update_guild_json(guild_id,savefile.setup_base_guild_savefile(guild_id,name=guild_name))

# Add the command structure to the bot.
bot.tree.add_command(admin_commands)
bot.tree.add_command(election_commands)
bot.tree.add_command(config_commands)
bot.tree.add_command(results_commands)

# on ready event.
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    savefile.load()
    for guild in bot.guilds:
        print(f"Checking guild {guild.name} ({guild.id})")
        __initialize_guild(guild.id, guild.name)
    for guild in bot.guilds:
        print(f'{bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})')
        synced = await bot.tree.sync()
        print(f"Synced! {len(synced)} commands(s)")

# Run the bot!
bot.run(TOKEN)