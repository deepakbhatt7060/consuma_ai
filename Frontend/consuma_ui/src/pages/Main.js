import { useContext, useState } from "react";
import { Container } from "../components/Container";
import { Table } from "../components/Table";
import { fetcher } from "../utils";

import { AppContext } from "../context/AppContext";

export const Main = () => {
  const { health, healthLoading, loading, setLoading } = useContext(AppContext);
  const [syncResult, setSyncResult] = useState(undefined);
  const [asyncResult, setAsyncResult] = useState(undefined);
  const [syncInput, setSyncInput] = useState("");
  const [asyncInput, setAsyncInput] = useState("");
  const [callbackURL, setCallbackURL] = useState("");
  const [requestId, setRequestId] = useState("");
  const [requestResponse, setRequestResponse] = useState(undefined);
  const [mode, setMode] = useState("");
  const [allRequestResponse, setAllRequestResponse] = useState(undefined);

  const BASE_URL = process.env.REACT_APP_API_BASE_URL;

  const displyArea = {
    minHeight: "600px",
    marginTop: "80px",
    borderRadius: "16px",
    padding: "24px",
    boxShadow: "0 4px 24px rgba(45, 108, 223, 0.1)",
  };

  const labelStyle = {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "8px",
  };

  const vrLine = {
    borderLeft: "1px solid black",
    height: "350px",
    margin: "0 20px",
  };

  const callAPI = async (type, e) => {
    e.preventDefault();
    let url = type === "sync" ? `${BASE_URL}/sync` : `${BASE_URL}/async`;
    let payload =
      type === "sync"
        ? { number: Number(syncInput) }
        : { number: Number(asyncInput), callback_url: callbackURL };
    setLoading(() => {
      if (type === "sync") {
        return "sync";
      } else {
        return "async";
      }
    });
    const response = await fetcher(url, "POST", payload);
    setLoading(undefined);
    console.log(`${type} response: `, response);
    if (type === "sync") {
      setSyncResult(response);
    } else {
      setAsyncResult(response);
    }
  };

  const getRequestDetails = async (e, all) => {
    e.preventDefault();
    if (!all) {
      if (!requestId) return;
      const url = `${BASE_URL}/requests/${requestId}`;
      const response = await fetcher(url, "GET");
      setRequestResponse(response);
    } else {
      if (!mode) return;
      const url = `${BASE_URL}/requests?mode=${mode}`;
      const response = await fetcher(url, "GET");
      setAllRequestResponse(response);
    }
  };
  return (
    <Container style={{ ...displyArea }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <div
          style={{
            backgroundColor: health?.status === "ok" ? "green" : "red",
            height: "16px",
            width: "16px",
            borderRadius: "50%",
          }}
        />
        <h3> Backend Health</h3> {healthLoading && "Loading..."}
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "40px",
        }}
      >
        <div
          style={{
            display: "flex",
            width: "100%",
            justifyContent: "space-evenly",
          }}
        >
          <form>
            <h3>Sync API Test</h3>
            <label style={labelStyle}>
              Synchronous nth Fibonacci Number Calculator
            </label>
            <input
              type="text"
              name="input"
              placeholder="Enter any number"
              onChange={(e) => setSyncInput(e.target.value)}
              value={syncInput}
            />

            <br />
            <br />
            <button onClick={(e) => callAPI("sync", e)}>Test Sync</button>
            <br />
            <br />
            <div>
              <h4>Answer: </h4>
              {loading === "sync" ? "Loading..." : syncResult?.output}
            </div>
          </form>
          <div style={vrLine} />
          <form>
            <h3>Async API Test</h3>
            <label style={labelStyle}>
              Asynchronous nth Fibonacci Calculator
            </label>
            <input
              type="text"
              name="input"
              placeholder="Enter any number"
              onChange={(e) => setAsyncInput(e.target.value)}
              value={asyncInput}
            />
            <br />
            <br />
            <input
              type="text"
              name="callback_url"
              placeholder="Enter Callback URL "
              onChange={(e) => setCallbackURL(e.target.value)}
              value={callbackURL}
            />
            <br />
            <br />
            <button onClick={(e) => callAPI("async", e)}>Test Async</button>
            <br />
            <br />
            <div>
              <h4>Answer: </h4>
              {loading === "async" ? (
                "Loading..."
              ) : asyncResult ? (
                <>
                  {asyncResult?.status} with Req. Id: <b>{asyncResult?.id}</b>
                </>
              ) : null}
            </div>
          </form>
        </div>
        <hr />
        <div style={{ padding: 20 }}>
          <form>
            <h3>Request Details by Request ID</h3>
            <label style={labelStyle}>Request ID</label>
            <input
              type="text"
              name="input"
              placeholder="Enter Request ID"
              onChange={(e) => setRequestId(e.target.value)}
              value={requestId}
            />
            <br />
            <br />
            <button onClick={(e) => getRequestDetails(e, false)}>Submit</button>
          </form>
          <div>
            {requestResponse && <Table requestResponse={requestResponse} />}
          </div>
        </div>
        <div style={{ padding: 20 }}>
          <form>
            <h3>Request Details by Mode</h3>
            <label style={labelStyle}>Enter Mode</label>
            <input
              type="text"
              name="input"
              placeholder="Enter Mode"
              onChange={(e) => setMode(e.target.value)}
              value={mode}
            />
            <br />
            <br />
            <button onClick={(e) => getRequestDetails(e, true)}>Submit</button>
          </form>
          <div>
            {allRequestResponse && (
              <Table requestResponse={allRequestResponse} list={true} />
            )}
          </div>
        </div>
      </div>
    </Container>
  );
};
