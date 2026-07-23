import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

function escapeQuotes(s: string): string {
  return s.replace(/'/g, "'\\''");
}

async function getOurTabName(cwd: string): Promise<string | null> {
  try {
    const { execSync } = await import("node:child_process");
    const escapedCwd = escapeQuotes(cwd);
    const tabName = execSync(
      `osascript -e '
        tell application "Ghostty"
          try
            set allTerms to terminals of first window
            repeat with t in allTerms
              if working directory of t = "${escapedCwd}" then
                return name of t
              end if
            end repeat
            return ""
          on error
            return ""
          end try
        end tell
      '`,
      { encoding: "utf-8", timeout: 3000 },
    ).trim();
    return tabName || null;
  } catch {
    return null;
  }
}

async function shouldNotify(cwd: string): Promise<boolean> {
  try {
    const { execSync } = await import("node:child_process");

    // Check if terminal app is frontmost
    const frontApp = execSync(
      `osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true'`,
      { encoding: "utf-8", timeout: 2000 },
    ).trim();

    const terminalApps = /^(terminal|iterm2|ghostty|kitty|wezterm)$/i;
    if (!terminalApps.test(frontApp)) {
      return true; // user is in a non-terminal app → notify
    }

    // Terminal is frontmost — check if OUR tab is focused
    // by comparing the focused terminal's cwd with ours
    const escapedCwd = escapeQuotes(cwd);
    const focusedCwd = execSync(
      `osascript -e '
        tell application "Ghostty"
          try
            set ft to focused terminal of selected tab of first window
            get working directory of ft
          on error
            return "__ERROR__"
          end try
        end tell
      '`,
      { encoding: "utf-8", timeout: 3000 },
    ).trim();

    // If focused terminal's cwd matches ours → same tab → no notification
    return focusedCwd !== cwd;
  } catch {
    return true; // can't determine, notify to be safe
  }
}

async function notify(title: string, body: string) {
  const { execSync } = await import("node:child_process");

  if (process.platform === "darwin") {
    execSync(
      `osascript -e 'display notification "${body.replace(/"/g, '\\"')}" with title "${title.replace(/"/g, '\\"')}" sound name "Ping"'`,
      { stdio: "ignore", timeout: 2000 },
    );
    return;
  }

  if (process.platform === "linux") {
    try {
      execSync(`notify-send "${title}" "${body}"`, {
        stdio: "ignore",
        timeout: 2000,
      });
      return;
    } catch {
      // fall through to terminal escape
    }
  }

  // Fallback: terminal OSC 777
  process.stdout.write(`\x1b]777;notify;${title};${body}\x07`);
}

let notified = false;

export default function (pi: ExtensionAPI) {
  pi.on("agent_settled", async () => {
    if (notified) return;
    notified = true;

    const cwd = process.cwd();
    if (await shouldNotify(cwd)) {
      const tabName = await getOurTabName(cwd);
      const body = tabName ? `Ready (${tabName})` : "Ready";
      notify("Pi", body);
    }
  });

  pi.on("session_start", () => {
    notified = false;
  });
}
