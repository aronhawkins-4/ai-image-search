import { GetResult, Metadata } from "chromadb";

export async function getImages(
  offset: number = 0,
): Promise<GetResult<Metadata>> {
  const response = await fetch(
    `http://localhost:8001/get-images?offset=${offset}`,
    {
      method: "GET",
      headers: {
        Authorization: "Bearer secret-token",
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to get images: ${response.statusText}`);
  }
  const data = await response.json();
  return data.results;
}
