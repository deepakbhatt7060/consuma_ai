export const Table = ({ requestResponse, list }) => {
  const theadings =
    list && requestResponse?.length > 0 ? requestResponse[0] : requestResponse;

  return (
    <table
      border="1"
      cellPadding="8"
      style={{
        borderCollapse: "collapse",
        tableLayout: "fixed",
        width: "100%",
      }}
    >
      <thead>
        <tr>
          {Object.keys(theadings).map((item) => {
            if (item === "result" || item === "payload") return null;
            return (
              <th
                key={item}
                style={{
                  fontWeight: "bold",
                  textAlign: "left",
                  wordBreak: "break-word",
                }}
              >
                {item}
              </th>
            );
          })}
        </tr>
      </thead>

      <tbody>
        {list ? (
          requestResponse.map((resp, index) => (
            <tr key={index}>
              {Object.keys(resp).map((item) => {
                if (item === "result" || item === "payload") return null;
                return (
                  <td key={item}>
                    <div
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        wordBreak: "break-word",
                        whiteSpace: "normal",
                      }}
                    >
                      {String(resp[item])}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))
        ) : (
          <tr>
            {Object.keys(requestResponse).map((item) => {
              if (item === "result" || item === "payload") return null;
              return (
                <td key={item}>
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      wordBreak: "break-word",
                      whiteSpace: "normal",
                    }}
                  >
                    {String(requestResponse[item])}
                  </div>
                </td>
              );
            })}
          </tr>
        )}
      </tbody>
    </table>
  );
};
