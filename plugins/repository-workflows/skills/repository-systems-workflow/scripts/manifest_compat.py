"""Portable Agent Plugins manifest plus the separate Codex compatibility overlay."""
SCHEMA='https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
VERSION='1.0.3'

def portable(name,title,description):
    return {'$schema':SCHEMA,'name':name,'version':VERSION,'description':description,
            'author':{'name':'WhiteChronos'},'license':'MIT',
            'repository':'https://github.com/WhiteChronos/ChatGPT',
            'extensions':{'com.openai':{'interface':{
                'displayName':title,'shortDescription':'Workflows por repositório',
                'longDescription':description+' Usa somente recursos disponíveis no host; instalação e execução requerem comprovação própria.',
                'developerName':'WhiteChronos','category':'Developer Tools',
                'defaultPrompt':['Use este workflow na tarefa e no repositório que eu indicar.']}}}}

def codex(portable_manifest):
    return {**{k:portable_manifest[k] for k in ('name','version','description','author','license','repository')},
            'skills':'./skills/','interface':portable_manifest['extensions']['com.openai']['interface']}
