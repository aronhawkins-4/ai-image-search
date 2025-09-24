import * as fs from 'fs'
import * as path from 'path'
import os from 'os'

const searchFiles = (dir: string, query: string, results: string[]): void => {
  try {
    const files = fs.readdirSync(dir)
    for (const file of files) {
      const filePath = path.join(dir, file)
      let stat
      try {
        stat = fs.statSync(filePath)
      } catch {
        continue // skip files we can't stat (permissions, etc)
      }
      if (stat.isDirectory()) {
        // Avoid searching system folders that may cause issues
        if (
          file === 'node_modules' ||
          file.startsWith('.') ||
          file === 'Library' ||
          file === 'AppData' ||
          file === 'Windows' ||
          file === 'System Volume Information'
        ) {
          continue
        }
        searchFiles(filePath, query, results)
      } else if (file.toLowerCase().includes(query.toLowerCase())) {
        results.push(filePath)
      }
    }
  } catch {
    // ignore directories we can't access
  }
}

const getRootDirs = (): string[] => {
  const platform = os.platform()
  if (platform === 'win32') {
    // On Windows, search all drives (C:\, D:\, etc.)
    return ['C:\\', 'D:\\', 'E:\\', 'F:\\', 'G:\\']
  } else {
    // On macOS/Linux, start from home directory
    return [os.homedir() + '/Downloads']
  }
}

export const searchFilesByName = async (query: string): Promise<string[]> => {
  const results: string[] = []
  const roots = getRootDirs()
  for (const root of roots) {
    searchFiles(root, query, results)
  }
  return results
}
