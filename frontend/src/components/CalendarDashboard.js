import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  Heading,
  useToast,
  Spinner,
  useDisclosure,
  Flex,
  Wrap,
  WrapItem
} from '@chakra-ui/react';
import { format, parseISO } from 'date-fns';
import { api } from '../api';
import { Calendar } from './Calendar';
import { EventDetailsModal } from './EventDetailsModal';

export function CalendarDashboard({ token, onLogout }) {
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [eventText, setEventText] = useState('');
  const [isParsing, setIsParsing] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [suggestedTimes, setSuggestedTimes] = useState([]);
  const [conflictingEventTitle, setConflictingEventTitle] = useState('');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  const fetchEvents = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.getEvents(token);
      setEvents(data);
    } catch (error) {
      toast({
        title: 'Error fetching events',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
    setIsLoading(false);
  }, [token, toast]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const handleParseEvent = async (textToParse = eventText) => {
    if (!textToParse.trim()) return;
    setIsParsing(true);
    setSuggestedTimes([]);
    
    if (!textToParse.startsWith('reschedule')) {
        setConflictingEventTitle('');
    }

    try {
      const result = await api.parseEvent(textToParse, token);
      
      if (result.is_conflict) {
        toast({
          title: 'Event Conflict',
          description: `This event conflicts with: ${result.conflict_details}. Here are some suggestions.`,
          status: 'warning',
          duration: 7000,
          isClosable: true,
        });
        setSuggestedTimes(result.suggested_times || []);
        setConflictingEventTitle(result.created_event.title);
      } else {
        toast({
          title: 'Event Processed',
          description: 'Event created successfully!',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        setEventText('');
        setConflictingEventTitle('');
      }
      
      fetchEvents();
    } catch (error) {
      toast({
        title: 'Error creating event',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
    setIsParsing(false);
  };
  
  const handleSuggestionClick = (time) => {
    const newText = `reschedule ${conflictingEventTitle} to ${format(parseISO(time), 'PPP p')}`;
    setEventText(newText);
    handleParseEvent(newText);
  };

  const handleEventClick = (event) => {
    setSelectedEvent(event);
    onOpen();
  };
  
  const handleEventUpdate = (updatedEvent) => {
    setEvents(prevEvents => prevEvents.map(e => e.id === updatedEvent.id ? updatedEvent : e));
    setSelectedEvent(updatedEvent);
  };
  
  const handleEventDelete = (deletedEventId) => {
    setEvents(prevEvents => prevEvents.filter(e => e.id !== deletedEventId));
  };

  return (
    <Box p={8}>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading>My Calendar</Heading>
        <Button onClick={onLogout}>Log Out</Button>
      </Flex>
      <VStack spacing={6}>
        <Box w="full" p={4} borderWidth={1} borderRadius={8} boxShadow="sm">
          <Text mb={2}>Create an event using natural language:</Text>
          <HStack>
            <Input
              placeholder="e.g., 'reschedule soccer practice to next Tuesday at 5pm at the park'"
              value={eventText}
              onChange={(e) => setEventText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleParseEvent()}
            />
            <Button colorScheme="teal" onClick={() => handleParseEvent()} isLoading={isParsing}>
              Create Event
            </Button>
          </HStack>
          {suggestedTimes.length > 0 && (
            <Box mt={4}>
                <Text mb={2} fontSize="sm" fontWeight="bold">Conflict detected. Try one of these times instead:</Text>
                <Wrap>
                    {suggestedTimes.map((time, index) => (
                        <WrapItem key={index}>
                            <Button size="sm" variant="outline" onClick={() => handleSuggestionClick(time)}>
                                {format(parseISO(time), 'EEE, p')}
                            </Button>
                        </WrapItem>
                    ))}
                </Wrap>
            </Box>
          )}
        </Box>
        {isLoading ? (
          <Spinner size="xl" />
        ) : (
          <Calendar events={events} onEventClick={handleEventClick} />
        )}
      </VStack>
      {selectedEvent && <EventDetailsModal isOpen={isOpen} onClose={onClose} event={selectedEvent} onUpdate={handleEventUpdate} onDelete={handleEventDelete} token={token} />}
    </Box>
  );
}
