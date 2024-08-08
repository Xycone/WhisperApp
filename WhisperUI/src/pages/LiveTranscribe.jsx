import React from 'react'

import { Box, Typography } from '@mui/material'

// React Components
import Header from '../components/Header';

function LiveTranscribe() {
    return (
        <Box p={5}>
            <Box
                display="flex"
                flexDirection="column"
            >
                <Header
                    title="Live Transcribe"
                    subtitle="[POST]: /live-transcribe"
                />

                <Box m={4}>
                    <Typography>Test</Typography>
                </Box>
            </Box>
        </Box>
    )
}

export default LiveTranscribe