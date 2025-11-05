# Testing Guide - Format Parameter Fix

## Important: Restart Required! 🔄

If you're seeing the error:
```
got multiple values for keyword argument 'format_types'
```
or
```
got multiple values for keyword argument 'format_type'
```

This means **the server is running old code**. You need to restart it!

## Quick Fix Steps

### Option 1: Use the Restart Script (Recommended)
```bash
./restart_server.sh
```

### Option 2: Manual Restart
```bash
# 1. Stop the running server
pkill -f "python.*main.py"

# 2. Start it again
python main.py
```

### Option 3: Using Ctrl+C
If you have the server running in a terminal:
1. Press `Ctrl+C` to stop it
2. Run `python main.py` again

## Verify the Fix

After restarting, verify the fix works:

```bash
# 1. Check server health
curl http://localhost:8000/health

# 2. Test with a simple query
curl -X POST http://localhost:8000/api/v1/math/solve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is 2 + 2?",
    "format": "latex",
    "show_steps": true
  }'
```

## Run the Full Test Suite

Once the server is restarted:

```bash
python test_format_parameter.py
```

## What Was Fixed?

The issue was that `query_classifier.get_api_params()` returns params containing:
- `format_types` for full_results API
- `format_type` for show_steps API
- `output_format` for language_eval API

And we were also passing these explicitly, causing "duplicate keyword argument" errors.

**Solution:** The `_call_wolfram_api()` function now filters out these keys from params before using `**params`, preventing conflicts.

## Troubleshooting

### Server won't stop
```bash
# Force kill all Python processes
pkill -9 -f "python.*main.py"
```

### Can't find process
```bash
# Find all Python processes
ps aux | grep python

# Or specifically for our server
ps aux | grep main.py
```

### Port already in use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Still getting errors after restart
1. Make sure you have the latest code:
   ```bash
   git pull origin claude/analyze-codebase-011CUoSNWxgJbkGSwTNeKsMK
   ```

2. Check the commit:
   ```bash
   git log --oneline -1
   # Should show: 75a15c7 Fix duplicate keyword argument error in _call_wolfram_api
   ```

3. Verify the fix is in the code:
   ```bash
   grep -A 3 "api_params = {k: v" routes/math.py
   ```

## Expected Test Results

After the fix and restart, you should see:
- ✓ All 25 problems processed (some may fail due to API limitations, but not due to duplicate argument errors)
- ✓ Solution files created in `answers/` folder
- ✓ Each solution with LaTeX formatting and step-by-step solutions
- ✓ Summary showing success rate

## Questions?

If you're still having issues:
1. Check that the server shows no errors in its output
2. Look at the server logs for any error messages
3. Verify the `answers/` folder is being created
4. Check individual solution files for specific error messages
