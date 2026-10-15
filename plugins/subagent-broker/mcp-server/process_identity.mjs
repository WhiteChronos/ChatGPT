import fs from 'node:fs/promises';
import { spawn } from 'node:child_process';
import {brokerError} from './protocol.mjs';

function capture(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { shell: false, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', chunk => stdout += chunk);
    child.stderr.on('data', chunk => stderr += chunk);
    child.on('error', reject);
    child.on('close', code => resolve({ code, stdout: stdout.trim(), stderr: stderr.trim() }));
  });
}

async function readWindowsProcessIdentity(pid) {
  const command = `$p=Get-Process -Id ${pid} -ErrorAction Stop; [Console]::Out.Write($p.StartTime.ToUniversalTime().Ticks)`;
  try {
    const result = await capture('powershell.exe', ['-NoLogo', '-NoProfile', '-NonInteractive', '-Command', command]);
    if (result.code !== 0 || !/^\d+$/.test(result.stdout)) return null;
    return { pid, start_ticks: result.stdout };
  } catch (error) {
    if (error?.code === 'ENOENT' || error?.code === 'ESRCH' || error?.code === 'EACCES') return null;
    throw error;
  }
}

export async function readProcessIdentity(pid) {
  const n=Number(pid);
  if(!Number.isInteger(n)||n<=0)return null;
  if (process.platform === 'win32') return readWindowsProcessIdentity(n);
  try {
    const text=await fs.readFile(`/proc/${n}/stat`,'utf8');
    const close=text.lastIndexOf(')');
    if(close<0)return null;
    const rest=text.slice(close+2).trim().split(/\s+/);
    // /proc/<pid>/stat field 22; rest[0] is field 3, so index 19 is field 22.
    const start_ticks=rest[19];
    if(!start_ticks)return null;
    return {pid:n,start_ticks:String(start_ticks)};
  } catch(error) {
    if(error?.code==='ENOENT'||error?.code==='ESRCH'||error?.code==='EACCES')return null;
    throw error;
  }
}

export const readLinuxProcessIdentity = readProcessIdentity;

export function isSameProcessIdentity(recorded,current){
  return Boolean(recorded&&current&&Number(recorded.pid)===Number(current.pid)&&String(recorded.start_ticks)===String(current.start_ticks));
}

export async function terminateProcessGroup(pid,signal='SIGTERM'){
  const n=Number(pid);if(!Number.isInteger(n)||n<=0)throw brokerError('INVALID_ARGUMENT','pid must be a positive integer');
  if (process.platform === 'win32') {
    const result = await capture('taskkill.exe', ['/PID', String(n), '/T', '/F']);
    if (result.code === 0) return true;
    if (!await readWindowsProcessIdentity(n)) return false;
    throw new Error(result.stderr || result.stdout || `taskkill failed with ${result.code}`);
  }
  try { process.kill(-n,signal); return true; }
  catch(error){ if(error?.code==='ESRCH')return false; throw error; }
}
