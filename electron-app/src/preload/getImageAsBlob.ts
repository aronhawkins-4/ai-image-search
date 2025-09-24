import fs from "fs";
import pathModule from "path";

// This handler reads an image file and returns its contents as a base64 string
export const getImageAsBlob = async (
  path: string,
): Promise<
  | { success: true; blob: string; error: null }
  | { success: false; blob: null; error: string }
> => {
  try {
    // Check if file exists and is accessible
    await fs.promises.access(path, fs.constants.R_OK);
    const stat = await fs.promises.stat(path);
    if (!stat.isFile()) {
      throw new Error("The provided path is not a file.");
    }

    // Optional: Limit file size to avoid memory issues (e.g., 50MB)
    const MAX_SIZE = 50 * 1024 * 1024;
    if (stat.size > MAX_SIZE) {
      throw new Error("File is too large to process as a blob.");
    }

    // Only allow image file extensions
    const allowedExts = [
      ".jpg",
      ".jpeg",
      ".png",
      ".gif",
      ".bmp",
      ".webp",
      ".tiff",
    ];
    const ext = pathModule.extname(path).toLowerCase();
    if (!allowedExts.includes(ext)) {
      throw new Error("Unsupported file type. Only image files are allowed.");
    }

    const data = await fs.promises.readFile(path);
    return { success: true, blob: data.toString("base64"), error: null };
  } catch (error) {
    return {
      success: false,
      blob: null,
      error: error instanceof Error ? error.message : String(error),
    };
  }
};
