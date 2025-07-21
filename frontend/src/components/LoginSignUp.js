import React, { useState } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Heading,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Flex,
} from '@chakra-ui/react';
import { api } from '../api';

export function LoginSignUp({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const data = await api.login(email, password);
      onLoginSuccess(data.access_token);
      toast({
        title: 'Login Successful',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Login Failed',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
    setIsLoading(false);
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await api.signUp(email, password);
      toast({
        title: 'Signup Successful',
        description: 'You can now log in with your credentials.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Signup Failed',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
    setIsLoading(false);
  };

  return (
    <Flex minH="100vh" align="center" justify="center" bg="gray.50">
      <Box p={8} maxWidth="400px" borderWidth={1} borderRadius={8} boxShadow="lg" bg="white">
        <Heading mb={6} textAlign="center">Family Assistant</Heading>
        <Tabs isFitted variant="enclosed">
          <TabList>
            <Tab>Login</Tab>
            <Tab>Sign Up</Tab>
          </TabList>
          <TabPanels>
            <TabPanel>
              <form onSubmit={handleLogin}>
                <VStack spacing={4}>
                  <Input placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                  <Input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                  <Button type="submit" colorScheme="teal" width="full" isLoading={isLoading}>
                    Login
                  </Button>
                </VStack>
              </form>
            </TabPanel>
            <TabPanel>
              <form onSubmit={handleSignUp}>
                <VStack spacing={4}>
                  <Input placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                  <Input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                  <Button type="submit" colorScheme="teal" width="full" isLoading={isLoading}>
                    Sign Up
                  </Button>
                </VStack>
              </form>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    </Flex>
  );
}
