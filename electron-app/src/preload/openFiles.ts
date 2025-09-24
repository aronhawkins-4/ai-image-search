import { shell } from "electron";

export const openFiles = async (
  paths: string[],
): Promise<{ message: string; paths: string[] }> => {
  try {
    const results = await Promise.all(
      paths.map((path) => shell.openPath(path)),
    );
    const failedPaths = paths.filter((_, index) => results[index]);
    if (failedPaths.length > 0) {
      // If there are failed paths, log the errors
      failedPaths.forEach((path, index) => {
        console.error("Failed to open path:", path, "Error:", results[index]);
      });
      return {
        message: "Error: Some files could not be opened",
        paths: failedPaths,
      };
    } else {
      return { message: "Success", paths };
    }
  } catch (error) {
    console.error("Exception opening paths:", paths, error);
    return {
      message:
        "Error: " + (error instanceof Error ? error.message : String(error)),
      paths,
    };
  }
};
