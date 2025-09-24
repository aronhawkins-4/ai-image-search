import { ElectronAPI } from "@electron-toolkit/preload";
import { GetResult, Metadata, QueryResult } from "chromadb";

declare global {
  interface Window {
    electron: ElectronAPI;
    api: {
      queryImages: (
        query: string,
        offset: number,
      ) => Promise<QueryResult<Metadata>>;
      getImages: (offset: number) => Promise<GetResult<Metadata>>;
      openFiles: (paths: string[]) => Promise<{
        message: string;
        paths: string[];
      }>;
      showFile: (path: string) => Promise<{
        message: string;
        path: string;
      }>;
      searchFilesByName: (query: string) => Promise<string[]>;
      getImageAsBlob: (path: string) => Promise<
        | {
            success: boolean;
            blob: string;
            error?: undefined;
          }
        | {
            success: boolean;
            error: string;
            blob?: undefined;
          }
      >;
      getDirectory: (
        path: string,
      ) => Promise<{ name: string; type: string; targetDir: string }[]>;
    };
  }
}
