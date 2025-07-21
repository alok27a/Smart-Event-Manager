import React, { useState } from 'react';
import {
  Box,
  VStack,
  Grid,
  Text,
  Heading,
  Tag,
  Flex,
  IconButton,
  Tooltip,
} from '@chakra-ui/react';
import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, parseISO } from 'date-fns';

// Map event categories to Chakra UI color schemes
const categoryColorMap = {
  SPORTS: 'green',
  APPOINTMENT: 'blue',
  SCHOOL: 'orange',
  WORK: 'purple',
  SOCIAL: 'pink',
  UNCATEGORIZED: 'gray',
};


export function Calendar({ events, onEventClick }) {
  const [currentDate, setCurrentDate] = useState(new Date());

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);

  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <Box w="full">
      <Flex justify="space-between" align="center" mb={4}>
        <IconButton icon={<ChevronLeftIcon />} onClick={() => setCurrentDate(subMonths(currentDate, 1))} aria-label="Previous month" />
        <Heading size="md">{format(currentDate, 'MMMM yyyy')}</Heading>
        <IconButton icon={<ChevronRightIcon />} onClick={() => setCurrentDate(addMonths(currentDate, 1))} aria-label="Next month" />
      </Flex>
      <Grid templateColumns="repeat(7, 1fr)" gap={1}>
        {weekdays.map(day => (
          <Text key={day} textAlign="center" fontWeight="bold" color="gray.500">{day}</Text>
        ))}
        {days.map(day => {
          const isCurrentMonth = isSameMonth(day, monthStart);
          const isToday = isSameDay(day, new Date());
          const dayEvents = events.filter(e => isSameDay(parseISO(e.start_time), day));

          return (
            <Box
              key={day.toString()}
              border="1px"
              borderColor="gray.200"
              bg={isToday ? 'teal.100' : 'white'}
              minH="120px"
              p={2}
              opacity={isCurrentMonth ? 1 : 0.4}
            >
              <Text fontWeight={isToday ? 'bold' : 'normal'}>{format(day, 'd')}</Text>
              <VStack align="start" spacing={1} mt={1}>
                {dayEvents.map(event => (
                  <Tooltip key={event.id} label={event.title}>
                    <Tag 
                      size="sm" 
                      variant="solid" 
                      colorScheme={categoryColorMap[event.category] || 'gray'}
                      onClick={() => onEventClick(event)} 
                      cursor="pointer"
                      w="full"
                      overflow="hidden"
                      textOverflow="ellipsis"
                      whiteSpace="nowrap"
                    >
                      {format(parseISO(event.start_time), 'p')} {event.title}
                    </Tag>
                  </Tooltip>
                ))}
              </VStack>
            </Box>
          );
        })}
      </Grid>
    </Box>
  );
}
