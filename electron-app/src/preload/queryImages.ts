import { Metadata, QueryResult } from "chromadb";

export async function queryImages(
  query: string,
  offset: number = 0,
): Promise<QueryResult<Metadata>> {
  const response = await fetch("http://localhost:8001/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      Authorization: "Bearer secret-token",
    },
    body: JSON.stringify({ query: query, offset: offset }),
  });

  if (!response.ok) {
    throw new Error(`Failed to query images: ${response.statusText}`);
  }
  const data = await response.json();
  return data.results;
}
