import { contextBridge } from "electron";
import { electronAPI } from "@electron-toolkit/preload";
import { queryImages } from "./queryImages";
import { openFiles } from "./openFiles";
import { showFile } from "./showFile";
import { searchFilesByName } from "./searchFilesByName";
import { getImageAsBlob } from "./getImageAsBlob";
import { getImages } from "./getImages";
import { getDirectory } from "./getDirectory";

// Custom APIs for renderer
const api = {
  queryImages: (query: string, offset: number) => queryImages(query, offset),
  getImages: (offset: number) => getImages(offset),
  openFiles: (paths: string[]) => openFiles(paths),
  showFile: (path: string) => showFile(path),
  searchFilesByName: (query: string) => searchFilesByName(query),
  getImageAsBlob: (path: string) => getImageAsBlob(path),
  getDirectory: (path: string) => getDirectory(path),
};

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld("electron", electronAPI);
    contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
} else {
  // @ts-ignore (define in dts)
  window.electron = electronAPI;
  // @ts-ignore (define in dts)
  window.api = api;
}
