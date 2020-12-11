# Tomi
A delightful discord extravaganza

## Set Up

`git clone https://github.com/mziv/Tomi && cd Tomi`

Download the tokens from the Google Drive folder. To get access, contact one of the admins. For development, you'll want to download `[TEST-TOMI-DELETE-THIS-PART].env` and rename it to `.env` and place it in the current folder. If you're running the production version, you'll download `[REAL-TOMI-DELETE-THIS-PART].env` and rename it to `.env`.

Then install requirements using `pip install -r requirements.txt` (or `conda env create --file requirements.txt` if you are using conda).

Some helpful commands:
`discord.utils.get(ctx.guild.roles, name="name_of_role")`: get a role
`ctx.guild.members`: get a list of members for a server
`member.roles`: get a list of roles for a member
