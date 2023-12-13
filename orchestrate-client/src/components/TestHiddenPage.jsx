/**
 * Hidden page module to test out Model component
 */
import React, {useEffect} from "react";

// import confirm dialog
// import Confirm from './Modal/Confirm';
import { Button, Paper, Typography, Modal} from "@mui/material"



export default function TestHiddenPage() {
    const [open, setOpen] = React.useState(true);
    const handleClose = () => setOpen(false);
    return (
        <div>
            <Modal
                open={open}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
            >
                <Paper component="form" 
                    className="flex-wrap justify-center h-35 w-200"
                >
                    <Typography id="modal-modal-title" variant="h6" component="h2">
                        Notice
                    </Typography>
                    <Typography id="modal-modal-description" sx={{ mt: 2 }}>
                        Music generation tools are trained on existing music pieces. 
                        Please be advised that this tour are not meant to be used for commercial purposes.  
                    </Typography>
                <Button onClick={handleClose}>Accept</Button>
                </Paper>
            </Modal>
            <h1>TestHiddenPage</h1>
            <p>You Have reach out hidden page</p>
        </div>
    )
}