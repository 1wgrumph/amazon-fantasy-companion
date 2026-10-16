package com.afc.companion.watch

import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.async
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** WatchActivity's switching confirmation: a destroyed activity resolves it as declined and closes its dialog. */
class SwitchPromptTest {
    @Test fun destroyClosesThePendingDialogAndDeclinesSoTheAttemptEnds() = runBlocking {
        val prompt = SwitchPrompt()
        var closed = 0
        val answer = async(start = CoroutineStart.UNDISPATCHED) { prompt.ask { { closed++ } } }
        assertFalse("waiting for the customer", answer.isCompleted)
        prompt.cancel()
        assertFalse("declined: no attempt, no report", answer.await())
        assertEquals("the dialog window is dismissed once", 1, closed)
        prompt.cancel()
        assertEquals(1, closed)
    }

    @Test fun askAfterDestroyShowsNothingAndDeclines() = runBlocking {
        val prompt = SwitchPrompt()
        prompt.cancel()
        var shown = false
        assertFalse(prompt.ask { shown = true; {} })
        assertFalse(shown)
    }

    @Test fun customerAnswerResolvesThePromptOnce() = runBlocking {
        val prompt = SwitchPrompt()
        var reply: ((Boolean) -> Unit)? = null
        val answer = async(start = CoroutineStart.UNDISPATCHED) { prompt.ask { r -> reply = r; {} } }
        checkNotNull(reply)(true)
        checkNotNull(reply)(false)
        assertTrue(answer.await())
        prompt.cancel()
    }
}
