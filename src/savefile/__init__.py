import json

save_file = {
}

ELECTIONS_COUNTER = 0
def reset_counters():
    ELECTIONS_COUNTER=0

def save():
    global save_file
    with open("savefile.json","w") as file:
        json.dump(save_file,file)
def load():
    global save_file
    with open("savefile.json","r") as file:
        save_file = json.load(file)
        
        # to update the elections counter to the highest election id
        global ELECTIONS_COUNTER
        for guild in save_file:
            for election in save_file[guild]["elections"]:
                if election["id"] > ELECTIONS_COUNTER:
                    ELECTIONS_COUNTER = election["id"]+1
        



def setup_base_guild_savefile(guildid,name="Guild"):
    return {
        "id":guildid,
        "name":name,
        "elections":[],
        "admin_roles":[],
        "candidacy_roles":[],
        "candidacy_perms_enabled":False,
        "voting_roles":[],
        "voting_perms_enabled":False,
        "voters":[],
        "candidates":[],
        "date":"N/A"
    }

def setup_base_election_savefile(electionid,name="Election",creator_id=-1):
    return {
        "id":electionid, # election id
        "name":name, # election name
        "candidates":[], # list of candidates
        "voters":[], # list of voters
        "voting_enabled":False, # is voting enabled
        "candidacy_enabled":False, # is candidacy enabled
        "candidacy_roles":[], # list of roles that can add candidates
        "voting_roles":[], # list of roles that can vote
        "candidacy_perms_enabled":False, # Are candidacy role restrictions enabled?
        "voting_perms_enabled":False, # Are voting role restrictions enabled?
        "creator":creator_id # creator of the election
    }


def update_guild_json(guildid,_json):
    load()
    global save_file
    save_file[str(guildid)] = _json
    save()


# check if file is defined if not then save, then load.
import os
if not os.path.exists("savefile.json"):
    save()
load()