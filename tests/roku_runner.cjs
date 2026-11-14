// Host adapter for Roku's single ifEnum cursor per object. No fish logic is duplicated.
const fs = require('node:fs');
const path = require('node:path');
const moduleRoot = process.env.BRS_BIN
  ? path.resolve(path.dirname(fs.realpathSync(process.env.BRS_BIN)), '..')
  : path.dirname(require.resolve('brs/package.json'));
const brs = require(path.join(moduleRoot, 'lib'));
const { Interpreter } = require(path.join(moduleRoot, 'lib/interpreter'));
const { Scope } = require(path.join(moduleRoot, 'lib/interpreter/Environment'));
const { Stmt } = require(path.join(moduleRoot, 'lib/parser'));
const cursors = new WeakMap();
const original = Interpreter.prototype.visitForEach;
Interpreter.prototype.visitForEach = function (statement) {
  const target = this.evaluate(statement.target);
  if (!brs.types.isIterable(target)) return original.call(this, statement);
  let cursor = cursors.get(target);
  if (!cursor) { cursor = { index: 0 }; cursors.set(target, cursor); }
  cursor.index = 0;
  while (cursor.index < target.getElements().length) {
    this.environment.define(Scope.Function, statement.item.text, target.getElements()[cursor.index]);
    try { this.execute(statement.body); }
    catch (error) {
      if (error instanceof Stmt.ExitForReason) break;
      throw error;
    }
    cursor.index += 1;
  }
  return brs.types.BrsInvalid.Instance;
};
const { Writable } = require('node:stream');
let transcript = '';
const capture = destination => new Writable({ write(chunk, encoding, done) {
  transcript += chunk.toString(); destination.write(chunk); done();
} });
const args = process.argv.slice(2);
const rootIndex = args.indexOf('--root');
const root = rootIndex >= 0 ? args.splice(rootIndex, 2)[1] : 'roku';
brs.execute(args, { root: path.resolve(root), stdout: capture(process.stdout), stderr: capture(process.stderr) })
  .then(() => { if (/^FAIL|not a function|Attempting to return|Syntax|error:/im.test(transcript)) process.exitCode = 1; })
  .catch(error => { console.error(error.messages?.join('\n') || error.message); process.exitCode = 1; });
