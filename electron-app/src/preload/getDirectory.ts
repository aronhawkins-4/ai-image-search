import fs from "node:fs";
import os from "node:os";

export const getDirectory = async (
  path: string,
): Promise<{ name: string; type: string; targetDir: string }[]> => {
  const targetDir = path.includes(os.homedir())
    ? path
    : `${os.homedir()}/${path}`;
  const entries = await fs.promises.readdir(targetDir, { withFileTypes: true });
  const imageExtensions = [".jpg", ".jpeg", ".png", ".webp", ".avif"];
  return entries
    .filter((entry) => {
      if (entry.name.startsWith(".") || entry.name.startsWith("$"))
        return false;
      if (entry.isDirectory()) return true;
      const ext = entry.name
        .toLowerCase()
        .substring(entry.name.lastIndexOf("."));
      return imageExtensions.includes(ext);
    })
    .map((entry) => ({
      name: entry.name,
      type: entry.isDirectory() ? "directory" : "file",
      targetDir: targetDir,
    }));
};
