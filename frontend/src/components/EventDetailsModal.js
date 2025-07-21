import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  Heading,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Tag,
  Textarea,
  NumberInput,
  NumberInputField,
    AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  useDisclosure
} from '@chakra-ui/react';
import { format, parseISO } from 'date-fns';
import { api } from '../api';

export function EventDetailsModal({ isOpen, onClose, event, onUpdate, onDelete, token }) {
    const [reminderMinutes, setReminderMinutes] = useState(30);
    const [shareEmail, setShareEmail] = useState('');
    const toast = useToast();
    const { isOpen: isAlertOpen, onOpen: onAlertOpen, onClose: onAlertClose } = useDisclosure();
    const cancelRef = React.useRef();

    if (!event) return null;

    const handleStatusChange = async (newState) => {
        try {
            const updatedEvent = await api.updateEventStatus(event.id, { state: newState }, token);
            onUpdate(updatedEvent);
            toast({ title: `Event marked as ${newState.toLowerCase()}`, status: 'success', duration: 2000 });
            onClose();
        } catch (error) {
            toast({ title: 'Error updating status', description: error.message, status: 'error', duration: 3000 });
        }
    };
    
    const handleAddReminder = async () => {
        try {
            const updatedEvent = await api.addReminder(event.id, { minutes_before: parseInt(reminderMinutes) }, token);
            onUpdate(updatedEvent);
            toast({ title: 'Reminder added', status: 'success', duration: 2000 });
        } catch (error) {
            toast({ title: 'Error adding reminder', description: error.message, status: 'error', duration: 3000 });
        }
    };

    const handleShare = async () => {
        if (!shareEmail) return;
        try {
            await api.shareEvent(event.id, [shareEmail], token);
            toast({ title: `Event shared with ${shareEmail}`, status: 'success', duration: 2000 });
            setShareEmail('');
        } catch (error) {
            toast({ title: 'Error sharing event', description: error.message, status: 'error', duration: 3000 });
        }
    };
    
    const handleDelete = async () => {
        try {
            await api.deleteEvent(event.id, token);
            onDelete(event.id);
            toast({ title: 'Event deleted', status: 'info', duration: 2000 });
            onAlertClose();
            onClose();
        } catch(error) {
            toast({ title: 'Error deleting event', description: error.message, status: 'error', duration: 3000 });
            onAlertClose();
        }
    };

    return (
        <>
            <Modal isOpen={isOpen} onClose={onClose} size="xl">
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>
                        <HStack>
                            <Text>{event.title}</Text>
                            <Tag colorScheme="teal" size="sm">{event.category}</Tag>
                            <Tag colorScheme="cyan" size="sm">{event.state}</Tag>
                        </HStack>
                    </ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <VStack align="start" spacing={4}>
                            <Text><strong>When:</strong> {format(parseISO(event.start_time), 'PPP p')} - {event.end_time ? format(parseISO(event.end_time), 'p') : ''}</Text>
                            {event.location && <Text><strong>Where:</strong> {event.location}</Text>}
                            {event.notes && <Box><strong>Notes:</strong><Textarea isReadOnly value={event.notes} mt={1} /></Box>}
                            
                            <Box w="full">
                                <Heading size="sm" mb={2}>Timeline</Heading>
                                <VStack align="start" spacing={1} pl={2} borderLeft="2px" borderColor="gray.200">
                                    {event.timeline.map((item, index) => (
                                        <Box key={index}>
                                            <Text fontSize="sm"><strong>{item.action}</strong> at {format(parseISO(item.timestamp), 'Pp')}</Text>
                                            {item.details && <Text fontSize="xs" color="gray.500">{item.details}</Text>}
                                        </Box>
                                    ))}
                                </VStack>
                            </Box>

                            <Box w="full">
                                <Heading size="sm" mb={2}>Reminders</Heading>
                                {event.reminders.length > 0 ? (
                                    <VStack align="start">
                                        {event.reminders.map((r, i) => <Text key={i}>- {r.minutes_before} minutes before</Text>)}
                                    </VStack>
                                ) : <Text fontSize="sm" color="gray.500">No reminders set.</Text>}
                                <HStack mt={2}>
                                    <NumberInput size="sm" value={reminderMinutes} onChange={(val) => setReminderMinutes(val)} min={1} max={10080}>
                                        <NumberInputField placeholder="Minutes before" />
                                    </NumberInput>
                                    <Button size="sm" onClick={handleAddReminder}>Add Reminder</Button>
                                </HStack>
                            </Box>
                            
                            <Box w="full">
                                <Heading size="sm" mb={2}>Share Event</Heading>
                                <HStack>
                                    <Input size="sm" placeholder="Email to share with" value={shareEmail} onChange={(e) => setShareEmail(e.target.value)} />
                                    <Button size="sm" onClick={handleShare}>Share</Button>
                                </HStack>
                            </Box>

                        </VStack>
                    </ModalBody>
                    <ModalFooter justifyContent="space-between">
                        <Button colorScheme="red" variant="outline" onClick={onAlertOpen}>Delete Event</Button>
                        <Box>
                            {event.state === 'DRAFT' && <Button colorScheme="green" mr={3} onClick={() => handleStatusChange('CONFIRMED')}>Confirm Event</Button>}
                            <Button variant="ghost" onClick={onClose}>Close</Button>
                        </Box>
                    </ModalFooter>
                </ModalContent>
            </Modal>

            <AlertDialog
                isOpen={isAlertOpen}
                leastDestructiveRef={cancelRef}
                onClose={onAlertClose}
            >
                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader fontSize="lg" fontWeight="bold">
                            Delete Event
                        </AlertDialogHeader>
                        <AlertDialogBody>
                            Are you sure? You can't undo this action afterwards.
                        </AlertDialogBody>
                        <AlertDialogFooter>
                            <Button ref={cancelRef} onClick={onAlertClose}>
                                Cancel
                            </Button>
                            <Button colorScheme="red" onClick={handleDelete} ml={3}>
                                Delete
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>
        </>
    );
}
