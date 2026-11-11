"""Select task-scoped workflows; never starts agents, shells, models or timers."""
import argparse
import json
from pathlib import Path

MODES=('auto','replica','superpowers','arena','combined')
INTENTS=('build-from-reference','feature','bugfix','compare','review','update','evolve-skills','deploy')
REPLICA={
    'build-from-reference':['replica-recon','replica-architect','replica-design','replica-build','replica-backend','replica-test','replica-diff'],
    'feature':['replica-architect','replica-build','replica-backend','replica-test'],
    'bugfix':['replica-test','replica-build','replica-test'],
    'compare':['replica-diff'], 'review':['replica-test','replica-diff'],
    'update':['replica-test'], 'evolve-skills':['replica-test'],
    'deploy':['replica-deploy'],
}
POWER={
    'build-from-reference':['brainstorming','writing-plans','test-driven-development','executing-plans','verification-before-completion','requesting-code-review'],
    'feature':['brainstorming','writing-plans','test-driven-development','executing-plans','verification-before-completion','requesting-code-review'],
    'bugfix':['systematic-debugging','test-driven-development','executing-plans','verification-before-completion','requesting-code-review'],
    'compare':['verification-before-completion'],
    'review':['requesting-code-review','verification-before-completion'],
    'update':['verification-before-completion','requesting-code-review'],
    'evolve-skills':['diagnosing-superpowers','writing-skills','verification-before-completion'],
    'deploy':['verification-before-completion','finishing-a-development-branch'],
}

def plan(mode,intent,complex_review=False):
    if mode not in MODES or intent not in INTENTS:
        raise ValueError('Use an explicit supported mode and intent; no arbitrary commands')
    selected=mode
    if mode=='auto':
        selected={'compare':'replica','review':'arena'}.get(intent,'combined')
    steps=[]
    def add(system,names,kind='skill'):
        steps.extend({'system':system,'kind':kind,'name':name} for name in names)
    if selected=='replica': add('replica',REPLICA[intent])
    elif selected=='superpowers': add('superpowers',POWER[intent])
    elif selected=='combined':
        names=POWER[intent]
        tail={'verification-before-completion','requesting-code-review','finishing-a-development-branch'}
        add('superpowers',[n for n in names if n not in tail])
        # Ordinary bugs/features/updates do not force application reconstruction.
        if intent in ('build-from-reference','compare','deploy'):
            add('replica',REPLICA[intent])
        add('superpowers',[n for n in names if n in tail])
    if selected in ('arena','combined'):
        if complex_review: add('arena',['arena_plan','arena_cards','arena_rubric'],'tool')
        add('arena',['arena_review_checklist'],'tool')
    return {'requested_mode':mode,'selected_mode':selected,'intent':intent,
            'steps':steps,'executed':False,'agents_started':False,'background_enabled':False,
            'status':'PLAN_ONLY','execution_owner':'current host agent',
            'reuse_current_artifacts':True,'same_failure_attempt_limit':2,
            'approval_scope':'Preserve user authorization; deployment and merge require their own authorized targets.'}

def doctor(selected,roots,available_tools=None):
    roots=[Path(root) for root in roots]
    skills=sorted({s['name'] for s in selected['steps'] if s['kind']=='skill'})
    required_tools=sorted({s['name'] for s in selected['steps'] if s['kind']=='tool'})
    found={name:str(next((r/name/'SKILL.md' for r in roots if (r/name/'SKILL.md').is_file()),'')) for name in skills}
    missing=[name for name,path in found.items() if not path]
    missing_tools=[] if available_tools is None else sorted(set(required_tools)-set(available_tools))
    status='BLOCKED' if missing or missing_tools else 'LOCAL_FILES_PRESENT'
    if status!='BLOCKED' and required_tools and available_tools is None:
        status='LOCAL_FILES_PRESENT_TOOLS_UNVERIFIED'
    return {'status':status,'skill_files':found,'missing_skills':missing,
            'required_tools':required_tools,'missing_tools':missing_tools,
            'host_discovery_verified':False,'execution_verified':False,
            'note':'File presence and supplied tool inventory do not prove model invocation or lifecycle execution.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('plan','doctor'))
    parser.add_argument('--system',choices=MODES,default='auto')
    parser.add_argument('--intent',choices=INTENTS,required=True)
    parser.add_argument('--complex',action='store_true')
    parser.add_argument('--skills-root',action='append',default=[])
    parser.add_argument('--available-tool',action='append',default=None)
    args=parser.parse_args()
    selected=plan(args.system,args.intent,args.complex)
    output=selected if args.action=='plan' else doctor(selected,args.skills_root,args.available_tool)
    print(json.dumps(output,ensure_ascii=False,indent=2))
    return 1 if output.get('status')=='BLOCKED' else 0

if __name__=='__main__': raise SystemExit(main())
