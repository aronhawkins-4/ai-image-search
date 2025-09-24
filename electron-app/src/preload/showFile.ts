import { shell } from "electron";
import fs from "fs";

export const showFile = async (
  path: string,
): Promise<{ message: string; path: string }> => {
  try {
    // Check if the file exists before showing it in the system file explorer
    if (!fs.existsSync(path)) {
      throw new Error("File does not exist: " + path);
    }
    shell.showItemInFolder(path);
    return { message: "Success", path };
  } catch (error) {
    console.error("Exception opening path:", path, error);
    return {
      message:
        "Error: " + (error instanceof Error ? error.message : String(error)),
      path,
    };
  }
};
