import fs from 'node:fs/promises';

export async function removeTree(root) {
  await fs.rm(root, {recursive:true, force:true, maxRetries:5, retryDelay:100});
}
