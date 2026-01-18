export const fetcher = async (url, method, payload) => {
  const options = payload
    ? {
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    : {};

  const response = await fetch(url, {
    method: method || "GET",
    ...options,
  });
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  return response.json();
};
