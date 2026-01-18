import { Applayout } from "./layouts/Applayout";
import { Container } from "./components/Container";

import { Main } from "./pages/Main";

import "./App.css";

function App() {
  return (
    <Applayout>
      <Container>
        <h1>Sync Async Test</h1>
      </Container>
      <Main />
    </Applayout>
  );
}

export default App;
