#!/usr/bin/env node
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const command = readFileSync(resolve(packageRoot, "shims", "thermos.md"), "utf8");

function usage() {
	console.log(`claude-thermos

Usage:
  claude-thermos install-command [--scope project|user] [--cwd <path>] [--dry-run]

Installs a standalone Claude Code /thermos command shim. The plugin-native command remains /thermos:run.`);
}

const args = process.argv.slice(2);
if (args.includes("--help") || args.includes("-h")) {
	usage();
	process.exit(0);
}

if (args[0] !== "install-command") {
	usage();
	process.exit(args.length === 0 ? 0 : 1);
}

let scope = "project";
let cwd = process.cwd();
let dryRun = false;

function readOptionValue(args, index, flag) {
	const value = args[index + 1];
	if (!value || value.startsWith("--")) {
		throw new Error(`${flag} requires a value`);
	}
	return value;
}

for (let i = 1; i < args.length; i++) {
	const arg = args[i];
	if (arg === "--scope") {
		scope = readOptionValue(args, i, arg);
		i++;
	} else if (arg === "--cwd") {
		cwd = resolve(readOptionValue(args, i, arg));
		i++;
	} else if (arg === "--dry-run") {
		dryRun = true;
	} else {
		throw new Error(`Unknown argument: ${arg}`);
	}
}

if (scope !== "project" && scope !== "user") {
	throw new Error(`--scope must be "project" or "user", got ${scope}`);
}

const targetDir = scope === "project" ? resolve(cwd, ".claude", "commands") : resolve(homedir(), ".claude", "commands");
const targetFile = resolve(targetDir, "thermos.md");

if (!dryRun) {
	mkdirSync(targetDir, { recursive: true });
	writeFileSync(targetFile, command);
}

console.log(`${dryRun ? "Would install" : "Installed"} /thermos shim at ${targetFile}`);
