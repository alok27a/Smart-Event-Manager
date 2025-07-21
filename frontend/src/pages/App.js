import ToggleTheme from "../components/ToggleTheme";
import React, { useState } from "react";
import { ChakraProvider, theme } from "@chakra-ui/react";
import { CalendarDashboard } from "../components/CalendarDashboard";
import { LoginSignUp } from "../components/LoginSignUp";

function App() {
  const [token, setToken] = useState(localStorage.getItem("authToken"));

  const handleLoginSuccess = (newToken) => {
    localStorage.setItem("authToken", newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    setToken(null);
  };

  return (
    <>
      {/* <ToggleTheme /> */}
      <ChakraProvider theme={theme}>
        {token ? (
          <CalendarDashboard token={token} onLogout={handleLogout} />
        ) : (
          <LoginSignUp onLoginSuccess={handleLoginSuccess} />
        )}
      </ChakraProvider>
    </>
  );
}

export default App;
