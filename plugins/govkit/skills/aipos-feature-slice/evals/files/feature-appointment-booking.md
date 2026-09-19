# Feature: Appointment booking (CLIN-302)

## Description

Patients book, and front-desk staff manage, clinic appointments online. Booking
must respect slot availability, appointment-type cutoffs, and patient privacy.
Reminders reduce no-shows.

## Acceptance Criteria

```gherkin
Feature: Appointment booking
  Patients book open clinic slots online, and the schedule stays consistent
  for staff and patients alike.

  Rule: A patient can book any open slot

    Scenario: Patient books an open appointment slot
      Given the clinic schedule shows an open slot on Tuesday at 10:00
      When the patient books that slot for a standard consultation
      Then the slot is confirmed as booked
      And the appointment appears in the patient's appointment list

  Rule: A slot can only be booked once

    Scenario: Double-booking is prevented
      Given another patient has already booked the Tuesday 10:00 slot
      When the patient attempts to book the same slot
      Then the booking is refused with a "slot no longer available" message
      And the slot is shown as unavailable

  Rule: Booking cutoffs depend on appointment type

    Scenario Outline: Booking is refused inside the cutoff window
      Given the current time is <hours_before> hours before the slot
      When the patient attempts to book a <appointment_type> appointment
      Then the booking is <outcome>

      Examples:
        | appointment_type | hours_before | outcome  |
        | standard         | 2            | refused  |
        | standard         | 30           | accepted |
        | procedure        | 30           | refused  |
        | procedure        | 80           | accepted |

  Rule: Patients receive a reminder before their appointment

    Scenario: Patient receives an SMS reminder 24 hours before the slot
      Given a patient has a confirmed appointment 24 hours from now
      And the patient has a verified mobile number on file
      When the reminder window opens
      Then the patient receives an SMS reminder via the clinic's SMS provider
      And the reminder is recorded on the appointment

  Rule: Staff can reschedule appointments

    Scenario: Front-desk staff reschedules by dragging on the calendar
      Given a confirmed appointment exists for Tuesday at 10:00
      When front-desk staff drags the appointment to Wednesday at 14:00 on the calendar
      Then the appointment is moved to Wednesday at 14:00
      And the patient is notified of the change by SMS

  Rule: Patients see only their own appointments

    Scenario: A patient cannot view another patient's appointments
      Given a patient is signed in
      When they request the appointment list of a different patient
      Then the request is refused with an authorization error
```

## NFRs

- Privacy: appointment data is patient-scoped; access control verified by
  automated authorization tests. Evidence: CI test results. Owner: Engineering.
- Reliability: reminder delivery is retried on SMS provider failure, up to 3
  attempts. Evidence: provider webhook logs in QA sign-off. Owner: Engineering.

## Evaluation Criteria

None. No AI or decision-support behavior; ordinary test evidence applies.

## Out of scope

- Video consultations
- Waiting-list management
